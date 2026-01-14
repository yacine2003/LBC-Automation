

import time
import random
import os
import sys
import base64
import hashlib
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TargetClosedError

import gsheet_manager
from config import (
    EMAIL, PASSWORD, LOGIN_URL, POST_AD_URL, COOKIE_FILE,
    MAX_ADS_PER_RUN, DELAY_BETWEEN_ADS_MIN, DELAY_BETWEEN_ADS_MAX,
    ENABLE_REAL_POSTING, SHEET_NAME, IMG_FOLDER,
    ACCOUNTS, NUM_ACCOUNTS  # Multi-comptes
)
from captcha_handler import CaptchaHandler

# Exception personnalisée pour l'arrêt du bot
class StopBotException(Exception):
    """Exception levée pour arrêter le bot proprement"""
    pass

def get_session_filename(email):
    """
    Génère un nom de fichier de session unique basé sur l'email
    Utilise un hash court pour éviter les conflits tout en restant lisible
    
    Args:
        email (str): Adresse email du compte
    
    Returns:
        str: Nom du fichier de session (ex: state_account_a1b2c3d4.json)
    """
    # Créer un hash MD5 de l'email et prendre les 8 premiers caractères
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()[:8]
    return f"state_account_{email_hash}.json"

class LBCPoster:
    def __init__(self, account=None, ws_callback=None, parent_instance=None):
        self.sheet_name = SHEET_NAME
        self.should_stop = False  # Flag for graceful shutdown
        self.ws_callback = ws_callback  # Callback pour WebSocket (optionnel)
        self.parent_instance = parent_instance  # Référence à l'instance parente pour partager le flag
        
        # Multi-comptes : Si un compte spécifique est fourni, l'utiliser
        if account:
            self.account = account
            self.email = account["email"]
            self.password = account["password"]
            self.account_number = account.get("account_number", 1)
        else:
            # Sinon utiliser le premier compte par défaut
            self.account = ACCOUNTS[0] if ACCOUNTS else None
            self.email = EMAIL
            self.password = PASSWORD
            self.account_number = 1 

    def send_ws_message(self, message_type, **kwargs):
        """Envoie un message via WebSocket si le callback est disponible"""
        if self.ws_callback:
            try:
                self.ws_callback({"type": message_type, **kwargs})
            except Exception as e:
                pass  # Pas grave si le WebSocket n'est pas disponible
    
    def log(self, message, level='info'):
        """Log un message dans la console et via WebSocket"""
        print(message)
        self.send_ws_message('log', message=message, level=level)

    def _check_should_stop(self):
        """Vérifie le flag d'arrêt (instance actuelle ou parente)"""
        if self.should_stop:
            return True
        if self.parent_instance and self.parent_instance.should_stop:
            return True
        return False
    
    def random_sleep(self, min_s=2.0, max_s=5.0):
        """Pause aléatoire avec vérification d'arrêt"""
        duration = random.uniform(min_s, max_s)
        print(f"   [Sleep] Pause de {duration:.2f}s...")
        
        # Sleep par petits incréments pour vérifier should_stop fréquemment
        elapsed = 0
        increment = 0.5  # Vérifie toutes les 0.5s
        while elapsed < duration:
            if self._check_should_stop():
                print("[Bot] ⏹ Arrêt demandé pendant le sleep.")
                raise StopBotException()  # Exception personnalisée pour sortir proprement
            time.sleep(min(increment, duration - elapsed))
            elapsed += increment

    def capture_screenshot(self, page):
        """Capture screenshot et encode en base64 pour streaming"""
        try:
            screenshot_bytes = page.screenshot()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return screenshot_base64
        except Exception as e:
            print(f"   ! Erreur capture screenshot : {e}")
            return None
    
    def check_stop(self, browser):
        """Vérifie si l'arrêt est demandé et termine proprement si oui"""
        if self._check_should_stop():
            print("[Bot] ⏹ Arrêt demandé par l'utilisateur.")
            try:
                browser.close()
            except:
                pass
            return True
        return False

    def human_type(self, page, selector, text, delay_min=0.1, delay_max=0.3):
        """Frappe au clavier humaine"""
        print(f"   [Typing] Écriture '{text}' dans {selector}...")
        try:
            element = page.locator(selector).first
            if not element.is_visible():
                print(f"   !!! Élément {selector} introuvable.")
                return

            element.click() 
            self.random_sleep(0.5, 1.0)
            
            for char in text:
                page.keyboard.type(char)
                time.sleep(random.uniform(delay_min, delay_max))
            
            self.random_sleep(0.5, 1.5)
        except Exception as e:
            print(f"   !!! Erreur frappe: {e}")

    def handle_cookies(self, page):
        """Gère la bannière"""
        print("   -> Vérif bannière Cookies...")
        try:
            accept_btn = page.get_by_role("button", name="Accepter & Fermer")
            accept_btn_alt = page.get_by_role("button", name="Tout accepter")

            if accept_btn.is_visible(timeout=3000):
                print("   -> Bannière cookies détectée : 'Accepter & Fermer'.")
                self.random_sleep(1, 2)
                accept_btn.click()
                print("   -> Clic effectué. Attente disparition bannière...")
                self.random_sleep(2, 3)  # Attente que la bannière disparaisse
                page.wait_for_load_state("domcontentloaded")
                return True
            elif accept_btn_alt.is_visible(timeout=1000):
                 print("   -> Bannière cookies détectée : 'Tout accepter'.")
                 self.random_sleep(1, 2)
                 accept_btn_alt.click()
                 print("   -> Clic effectué. Attente disparition bannière...")
                 self.random_sleep(2, 3)  # Attente que la bannière disparaisse
                 page.wait_for_load_state("domcontentloaded")
                 return True
            print("   -> Pas de bannière cookies visible.")
            return False
        except Exception as e:
            print(f"   -> Gestion cookies : {e}")
            return False

    def perform_login(self, page):
        """Flux de login complet"""
        print("--- LOGIN FLOW ---")
        page.wait_for_load_state("domcontentloaded")
        self.random_sleep(2, 3)
        self.handle_cookies(page)

        # 1. Email
        print(f"   -> Email ({self.email})...")
        try:
            email_sel = "input[name='email']"
            page.wait_for_selector(email_sel, timeout=5000)
            self.human_type(page, email_sel, self.email, 0.08, 0.25)
        except:
            print("   !!! Email introuvable.")
            return

        # 2. Continuer
        print("   -> Continuer...")
        try:
            cont_btn = page.get_by_role("button", name="Continuer").first
            if cont_btn.is_visible():
                self.random_sleep(1, 2)
                cont_btn.click()
            else:
                # Fallback
                sbmt = page.locator("button[type='submit']").first
                if sbmt.is_visible(): sbmt.click()
        except Exception as e:
            print(f"   !!! Erreur Continuer: {e}")

        # 3. Password
        print("   -> Password...")
        try:
            pass_sel = "input[name='password']"
            page.wait_for_selector(pass_sel, timeout=10000)
            self.human_type(page, pass_sel, self.password, 0.08, 0.25)
        except:
            print("   !!! Password introuvable.")
            return

        # 4. Submit
        print("   -> Se connecter...")
        try:
            self.handle_cookies(page)
            sign_btn = page.get_by_role("button", name="Se connecter").or_(page.locator("button[type='submit']")).first
            if sign_btn.is_visible():
                self.random_sleep(1, 2)
                sign_btn.click()
            else:
                page.keyboard.press("Enter")
        except:
            pass
        
        print("   -> Attente redirection...")
        page.wait_for_timeout(5000)

    def start_process(self, streaming_callback=None):
        """
        Point d'entrée principal - Gère la publication de plusieurs annonces
        
        Args:
            streaming_callback: Fonction async appelée avec les screenshots (optionnel)
        """
        print("=" * 80)
        print(f">>> DÉMARRAGE SESSION - Limite: {MAX_ADS_PER_RUN} annonces par session")
        print("=" * 80)
        
        # 🔍 VALIDATION : Vérifier que IMG_FOLDER est configuré
        if not IMG_FOLDER or IMG_FOLDER.strip() == "":
            error_msg = (
                "\n❌ ERREUR DE CONFIGURATION ❌\n"
                "Le dossier des photos (IMG_FOLDER) n'est pas configuré !\n\n"
                "👉 Pour configurer :\n"
                "   1. Ouvrez http://localhost:8000/config-page\n"
                "   2. Remplissez le champ '📁 Dossier des photos'\n"
                "   3. Exemple : C:/Photos/LBC ou /Users/VotreNom/Photos\n"
                "   4. Cliquez sur 'Enregistrer'\n"
            )
            print(error_msg)
            self.log(error_msg, 'error')
            return "ERROR_CONFIG_IMG_FOLDER_MISSING"
        
        print(f"✅ Dossier photos configuré : {IMG_FOLDER}")
        self.log(f"Dossier photos : {IMG_FOLDER}", 'info')
        
        ads_published = 0
        results = []
        
        # Connexion au Sheet une seule fois
        try:
            sheet = gsheet_manager.connect_to_sheets(self.sheet_name)
        except Exception as e:
            print(f"!!! Erreur connexion Sheet: {e}")
            return f"ERROR_SHEET_{e}"
        
        # Boucle de publication
        while ads_published < MAX_ADS_PER_RUN:
            if self._check_should_stop():
                print("[Session] ⏹ Arrêt demandé par l'utilisateur.")
                break
            
            print(f"\n{'=' * 80}")
            print(f">>> ANNONCE {ads_published + 1}/{MAX_ADS_PER_RUN}")
            print(f"{'=' * 80}\n")
            
            # Chercher la prochaine annonce à publier
            try:
                ad_data, row_num = gsheet_manager.get_next_ad_to_publish(sheet)
                if not ad_data:
                    print(">>> Plus d'annonces à publier (toutes sont FAIT).")
                    break
                print(f">>> Annonce trouvée : {ad_data.get('Titre')} (ligne {row_num})")
            except Exception as e:
                print(f"!!! Erreur lecture Sheet: {e}")
                break
            
            # Publier l'annonce
            result = self.publish_single_ad(ad_data, row_num, sheet, streaming_callback)
            results.append({"ad": ad_data.get('Titre'), "result": result})
            
            # Si publication réussie, marquer comme FAIT
            if result.startswith("SUCCESS"):
                try:
                    gsheet_manager.mark_ad_as_published(sheet, row_num)
                    ads_published += 1
                    print(f"✅ Annonce publiée avec succès ! ({ads_published}/{MAX_ADS_PER_RUN})")
                except Exception as e:
                    print(f"⚠️ Erreur mise à jour statut: {e}")
            else:
                print(f"❌ Échec publication : {result}")
                break  # On arrête en cas d'erreur
            
            # Délai entre annonces (sauf pour la dernière)
            if ads_published < MAX_ADS_PER_RUN and ads_published < len(results):
                delay = random.uniform(DELAY_BETWEEN_ADS_MIN, DELAY_BETWEEN_ADS_MAX)
                minutes = delay / 60
                print(f"\n⏳ Pause de {minutes:.1f} minutes avant la prochaine annonce...")
                try:
                    self.random_sleep(delay, delay + 10)
                except StopBotException:
                    print("[Session] ⏹ Arrêt demandé pendant la pause.")
                    break
        
        # Résumé final
        print("\n" + "=" * 80)
        print(f">>> SESSION TERMINÉE - {ads_published} annonce(s) publiée(s)")
        print("=" * 80)
        for r in results:
            status = "✅" if r["result"].startswith("SUCCESS") else "❌"
            print(f"  {status} {r['ad']}: {r['result']}")
        print("=" * 80 + "\n")
        
        return f"SESSION_COMPLETE_{ads_published}_ADS"
    
    def start_multi_account_process(self, streaming_callback=None):
        """
        NOUVELLE MÉTHODE : Gère la publication avec rotation entre plusieurs comptes
        Chaque compte publie MAX_ADS_PER_RUN annonces, puis passe au compte suivant
        """
        print("=" * 80)
        print(f"🎯 DÉMARRAGE SESSION MULTI-COMPTES")
        print(f"   Comptes configurés : {NUM_ACCOUNTS}")
        print(f"   Annonces par compte : {MAX_ADS_PER_RUN}")
        print("=" * 80)
        
        # Validation IMG_FOLDER
        if not IMG_FOLDER or IMG_FOLDER.strip() == "":
            error_msg = (
                "\n❌ ERREUR DE CONFIGURATION ❌\n"
                "Le dossier des photos (IMG_FOLDER) n'est pas configuré !\n\n"
                "👉 Pour configurer :\n"
                "   1. Ouvrez http://localhost:8000/config-page\n"
                "   2. Remplissez le champ '📁 Dossier des photos'\n"
                "   3. Cliquez sur 'Enregistrer'\n"
            )
            print(error_msg)
            self.log(error_msg, 'error')
            return "ERROR_CONFIG_IMG_FOLDER_MISSING"
        
        print(f"✅ Dossier photos configuré : {IMG_FOLDER}")
        self.log(f"Dossier photos : {IMG_FOLDER}", 'info')
        
        # Connexion au Sheet une seule fois
        try:
            sheet = gsheet_manager.connect_to_sheets(self.sheet_name)
        except Exception as e:
            print(f"!!! Erreur connexion Sheet: {e}")
            return f"ERROR_SHEET_{e}"
        
        total_published = 0
        account_stats = {account['email']: 0 for account in ACCOUNTS}  # Stats par compte
        
        # Rotation infinie des comptes jusqu'à épuisement des annonces
        account_index = 0  # Index du compte actuel (0-based)
        rotation_count = 0  # Compteur de rotations complètes
        
        while True:
            if self._check_should_stop():
                print(f"\n[Session] ⏹ Arrêt demandé par l'utilisateur.")
                break
            
            # Vérifier s'il reste des annonces à publier AVANT de commencer
            ad_data, _ = gsheet_manager.get_next_ad_to_publish(sheet)
            if not ad_data:
                print(f"\n>>> ✅ Plus d'annonces à publier ! Arrêt.")
                break
            
            # Sélectionner le compte en rotation
            current_account = ACCOUNTS[account_index]
            account_number = account_index + 1
            
            # Si on revient au premier compte après avoir utilisé tous les comptes
            if account_index == 0 and total_published > 0:
                rotation_count += 1
                print(f"\n{'=' * 80}")
                print(f"🔄 ROTATION {rotation_count + 1} - Retour au premier compte")
                print(f"{'=' * 80}")
            
            print("\n" + "=" * 80)
            print(f"👤 COMPTE {account_number}/{NUM_ACCOUNTS} : {current_account['email']}")
            if account_stats[current_account['email']] > 0:
                print(f"   (Déjà publié : {account_stats[current_account['email']]} annonce(s) lors des rotations précédentes)")
            print("=" * 80)
            
            # Créer une instance du poster pour ce compte avec référence à l'instance parente
            poster = LBCPoster(account=current_account, ws_callback=self.ws_callback, parent_instance=self)
            
            # Ce compte publie MAX_ADS_PER_RUN annonces
            result = poster.start_process_single_account(sheet, streaming_callback)
            
            # Compter les annonces publiées
            if "SUCCESS" in result or "COMPLETE" in result:
                import re
                match = re.search(r'(\d+)_ADS', result)
                if match:
                    ads_count = int(match.group(1))
                    total_published += ads_count
                    account_stats[current_account['email']] += ads_count
            
            # Passer au compte suivant (rotation circulaire)
            account_index = (account_index + 1) % NUM_ACCOUNTS
            
            # Vérifier s'il reste des annonces pour le prochain compte
            ad_data, _ = gsheet_manager.get_next_ad_to_publish(sheet)
            if not ad_data:
                print(f"\n>>> ✅ Plus d'annonces à publier ! Arrêt.")
                break
            
            # Délai entre comptes
            delay = random.uniform(90, 150)  # 1.5-2.5 minutes entre comptes
            minutes = delay / 60
            print(f"\n⏳ Pause de {minutes:.1f} minutes avant le prochain compte...")
            try:
                self.random_sleep(delay, delay + 30)
            except StopBotException:
                print("[Session] ⏹ Arrêt demandé pendant la pause.")
                break
        
        # Résumé final multi-comptes
        print("\n" + "=" * 80)
        print(f"🎉 SESSION MULTI-COMPTES TERMINÉE")
        print(f"   Total annonces publiées : {total_published}")
        print(f"   Rotations effectuées : {rotation_count + 1}")
        print("=" * 80)
        
        for account_email, count in account_stats.items():
            if count > 0:
                print(f"  ✅ {account_email}: {count} annonce(s)")
        
        print("=" * 80 + "\n")
        
        accounts_used = sum(1 for count in account_stats.values() if count > 0)
        return f"MULTI_ACCOUNT_COMPLETE_{total_published}_ADS_{accounts_used}_ACCOUNTS"
    
    def start_process_single_account(self, sheet, streaming_callback=None):
        """
        Version simplifiée pour un seul compte (utilisée dans la rotation multi-comptes)
        Publie MAX_ADS_PER_RUN annonces pour ce compte uniquement
        """
        print(f"📧 Connexion avec : {self.email}")
        self.log(f"Compte : {self.email}", 'info')
        
        ads_published = 0
        results = []
        
        # Boucle de publication pour ce compte
        while ads_published < MAX_ADS_PER_RUN:
            if self._check_should_stop():
                print("[Session] ⏹ Arrêt demandé.")
                break
            
            # Chercher la prochaine annonce
            try:
                ad_data, row_num = gsheet_manager.get_next_ad_to_publish(sheet)
                if not ad_data:
                    print(">>> Plus d'annonces disponibles.")
                    break
                ad_title = ad_data.get('Titre', 'Sans titre')
                print(f"\n📝 Annonce {ads_published + 1}/{MAX_ADS_PER_RUN}: {ad_title}")
                
                # Notifier le frontend du début de publication
                self.send_ws_message('ad_start', ad_title=ad_title, ad_number=ads_published + 1)
                
            except Exception as e:
                print(f"!!! Erreur lecture Sheet: {e}")
                break
            
            # Publier l'annonce
            result = self.publish_single_ad(ad_data, row_num, sheet, streaming_callback)
            results.append({"ad": ad_data.get('Titre'), "result": result})
            
            # Marquer comme FAIT si succès
            if result.startswith("SUCCESS"):
                try:
                    gsheet_manager.mark_ad_as_published(sheet, row_num)
                    ads_published += 1
                    print(f"✅ Publié ! ({ads_published}/{MAX_ADS_PER_RUN})")
                    
                    # Notifier le frontend de la publication réussie
                    self.send_ws_message('ad_complete', 
                                        ad_title=ad_data.get('Titre', 'Sans titre'),
                                        total_published=ads_published)
                except Exception as e:
                    print(f"⚠️ Erreur mise à jour statut: {e}")
            else:
                print(f"❌ Échec : {result}")
                break
            
            # Délai entre annonces (sauf pour la dernière)
            if ads_published < MAX_ADS_PER_RUN:
                delay = random.uniform(DELAY_BETWEEN_ADS_MIN, DELAY_BETWEEN_ADS_MAX)
                minutes = delay / 60
                print(f"\n⏳ Pause de {minutes:.1f} minutes avant la prochaine annonce...")
                try:
                    self.random_sleep(delay, delay + 10)
                except StopBotException:
                    print("[Session] ⏹ Arrêt demandé pendant la pause.")
                    break
        
        # Résumé pour ce compte
        print(f"\n>>> Compte {self.email} : {ads_published} annonce(s) publiée(s)")
        
        return f"ACCOUNT_COMPLETE_{ads_published}_ADS"
    
    def publish_single_ad(self, ad_data, row_num, sheet, streaming_callback=None):
        """
        Publie une seule annonce sur LeBonCoin
        
        Args:
            ad_data: Données de l'annonce depuis le Sheet
            row_num: Numéro de ligne dans le Sheet
            sheet: Instance du Sheet Google
            streaming_callback: Callback optionnel pour le streaming
        
        Returns:
            Code de résultat (SUCCESS_*, FAILURE_*, STOPPED_BY_USER)
        """
        # Générer un nom de fichier de session unique basé sur l'email
        account_cookie_file = get_session_filename(self.email)
        
        # 2. Playwright
        with sync_playwright() as p:
            print("[Browser] Launching...")
            browser = p.chromium.launch(
                headless=False, # Pour qu'on voie ce qui se passe sur le serveur
                args=["--disable-blink-features=AutomationControlled"]
            )
            context_args = {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "viewport": {"width": 1280, "height": 720},
                "locale": "fr-FR",
                "permissions": [] # On bloque la géolocalisation pour éviter les popups
            }

            # Charger la session spécifique à ce compte
            if os.path.exists(account_cookie_file):
                print(f"[Session] Chargement session pour {self.email} ({account_cookie_file})")
                context = browser.new_context(storage_state=account_cookie_file, **context_args)
            else:
                print(f"[Session] Nouvelle session pour {self.email}")
                context = browser.new_context(**context_args)

            try:
                from playwright_stealth import stealth_sync
                page = context.new_page()
                stealth_sync(page)
            except:
                page = context.new_page()

            try:
                # Navigation avec timeout augmenté et système de réessai
                print(f"[Nav] Vers {POST_AD_URL}")
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        page.goto(POST_AD_URL, timeout=60000)  # 60 secondes au lieu de 30
                        page.wait_for_load_state("domcontentloaded")
                        break  # Succès, on sort de la boucle
                    except Exception as nav_error:
                        if attempt < max_retries - 1:
                            print(f"[Nav] ⚠️ Timeout (tentative {attempt + 1}/{max_retries}), réessai dans 5s...")
                            self.random_sleep(5, 7)
                        else:
                            raise nav_error  # Dernière tentative échouée, on lève l'erreur
                
                self.random_sleep(2, 4)
                self.handle_cookies(page)
                
                # Pause importante après gestion cookies pour laisser la page se stabiliser
                print("   -> Attente stabilisation page après cookies...")
                self.random_sleep(3, 5)
                page.wait_for_load_state("networkidle", timeout=10000)

                # Login Check
                login_needed = False
                if "connexion" in page.url or "login" in page.url: login_needed = True
                
                if not login_needed:
                    # Double check content
                    cnt = page.content()
                    if "Me connecter" in cnt or "Connectez-vous" in cnt:
                        login_needed = True
                
                if login_needed:
                    print("[Login] Connexion requise...")
                    try:
                        # On attend que le header soit complètement chargé
                        print("   -> Attente chargement complet du header...")
                        self.random_sleep(2, 3)
                        
                        btn = page.locator("button, a").filter(has_text="Me connecter").first
                        btn.wait_for(state="visible", timeout=5000)
                        
                        # Pause avant de cliquer sur "Me connecter"
                        print("   -> Bouton 'Me connecter' détecté. Attente avant clic...")
                        self.random_sleep(2, 3)
                        
                        btn.click()
                        
                        self.perform_login(page)
                        
                        # Vérification captcha après connexion
                        captcha_handler = CaptchaHandler()
                        if not captcha_handler.check_at_key_moments(page, "après connexion"):
                            print("[Login] ❌ Échec résolution captcha après connexion")
                            return "CAPTCHA_FAILED_AFTER_LOGIN"
                        
                        # Sauvegarder la session spécifique à ce compte
                        context.storage_state(path=account_cookie_file)
                        print(f"[Session] Session pour {self.email} sauvegardée dans {account_cookie_file}")

                        print("[Nav] Retour Dépôt...")
                        page.wait_for_load_state("domcontentloaded")
                        self.random_sleep(2, 3)
                    except:
                        print("Could not click login button or login failed. Continuing anyway...")
                    if "deposer" not in page.url: 
                        page.goto(POST_AD_URL, timeout=60000)  # 60 secondes
                
                # Vérification captcha après navigation
                captcha_handler = CaptchaHandler()
                if not captcha_handler.check_at_key_moments(page, "sur page dépôt d'annonce"):
                    print("[Nav] ❌ Échec résolution captcha sur page dépôt")
                    return "CAPTCHA_FAILED_ON_DEPOSIT_PAGE"

                # Remplissage
                self.random_sleep(1, 2)
                print("[Form] Remplissage Titre...")
                
                filled = False
                result = "FAILURE_FORM_NOT_FOUND"  # Par défaut
                title_txt = str(ad_data.get('Titre'))
                
                # Essai 1 : Input subject
                inp = page.locator("input[name='subject']").first
                if inp.is_visible():
                    self.human_type(page, "input[name='subject']", title_txt)
                    filled = True
                
                # Essai 2 : Label
                if not filled:
                    try:
                        page.get_by_label("titre", exact=False).first.fill(title_txt)
                        filled = True
                    except: pass

                if filled:
                    print(f">>> SUCCES : Titre '{title_txt}' injecté !")
                    
                    # Check stop flag
                    if self.check_stop(browser):
                        return "STOPPED_BY_USER"
                    
                    # --- GESTION CATEGORIE ---
                    print("[Form] Attente des suggestions de catégorie...")
                    self.random_sleep(2, 4) # Laisser le temps à LBC de charger les suggestions
                    
                    # Récupérer la catégorie souhaitée du Sheet
                    target_cat = str(ad_data.get('Categorie', '')).strip().lower()
                    print(f"   -> Cible Sheet : '{target_cat}'")

                # Les suggestions sont souvent des div/boutons radio ou des éléments cliquables
                # On cherche les conteneurs de texte de suggestion
                # Sélecteur générique souvent utilisé : class qui contient 'create-classified-category-suggestion'
                # Ou simplement chercher le texte visible sous "Choisissez une catégorie suggérée"
                
                try:
                    # On attend qu'au moins une suggestion apparaisse
                    page.wait_for_selector("text=Choisissez une catégorie suggérée", timeout=10000)
                    
                    # On cherche tous les labels ou div qui pourraient être des suggestions
                    # Stratégie : On cherche tout texte qui suit le titre "Choisissez..."
                    # Plus robuste : Trouver les éléments cliquables dans la zone de suggestion
                    
                    # On va scanner les textes visibles
                    suggestions = page.locator("div[class*='CategorySuggestion'], label").all()
                    
                    clicked_cat = False
                    
                    # 1. Recherche Match
                    if target_cat:
                        for sugg in suggestions:
                            if not sugg.is_visible(): continue
                            txt = sugg.inner_text().lower()
                            if target_cat in txt:
                                print(f"   -> MATCH TROUVÉ SUGGESTION : '{txt}'. Clic !")
                                self.random_sleep(1, 3) # Hésitation avant clic
                                sugg.click()
                                clicked_cat = True
                                break
                    
                    # 2. Fallback: Chercher dans le menu déroulant "Autre catégorie"
                    if not clicked_cat:
                        print(f"   -> Pas de suggestion directe pour '{target_cat}'. Tentative Menu Déroulant...")
                        # "Choisissez une autre catégorie" ou ressemblant
                        # On cherche un bouton ou div qui ressemble à un select
                        dropdown = page.locator("div[class*='Select__Control'], button[class*='select']").filter(has_text="Choisissez").last
                        
                        if dropdown.is_visible():
                            print("   -> Menu déroulant trouvé. Ouverture...")
                            self.random_sleep(1, 2)
                            dropdown.click()
                            self.random_sleep(1, 2) # Temps que la liste s'ouvre
                            
                            # On tape la catégorie pour filtrer (si possible) ou on cherche dans la liste
                            if target_cat:
                                print(f"   -> Recherche '{target_cat}' dans la liste...")
                                page.keyboard.type(target_cat)
                                self.random_sleep(1, 2)
                                page.keyboard.press("Enter")
                                clicked_cat = True
                                print("   -> Tentative sélection menu (Entrée).")
                            else:
                                # Si pas de cat spécifiée, on clique un peu au hasard ou on annule
                                # Ici on suppose qu'il faut en choisir une.
                                pass 
                        else:
                            print("   x Menu déroulant 'Choisissez' non trouvé.")

                    # 3. Dernier Recours : La première suggestion
                    if not clicked_cat:
                        print("   -> Fallback Ultime : Clic sur la 1ère suggestion par défaut.")
                        # On re-scan pour être sûr d'avoir le premier visible
                        first_sugg = page.locator("div[class*='CategorySuggestion']").first
                        if not first_sugg.is_visible():
                             first_sugg = page.locator("label").nth(1) 
                        
                        if first_sugg.is_visible():
                            self.random_sleep(1, 3) 
                            first_sugg.click()
                            print("   -> 1ère suggestion cliquée.")
                            clicked_cat = True
                        else:
                            print("   !!! Impossible de trouver une suggestion cliquable.")

                    if clicked_cat:
                        print("   -> Catégorie validée.")
                        self.random_sleep(1, 2)
                        
                        # Check stop flag
                        if self.check_stop(browser):
                            return "STOPPED_BY_USER"
                        
                        # --- SUITE DU FORMULAIRE : BOUTON CONTINUER ---
                        # Une fois titre + catégorie mis, il faut souvent faire "Continuer"
                        print("[Form]  Clic 'Continuer' pour aller à la suite...")
                        next_btn = page.get_by_role("button", name="Continuer").last
                        if next_btn.is_visible():
                            next_btn.click()
                        else:
                            print("   (Pas de bouton Continuer vu, peut-être défilement auto ?)")

                except Exception as e:
                    print(f"   !!! Erreur Catégorie : {e}")

                # --- PHOTOS ---
                self.random_sleep(2, 3)
                print(f"[Form] Gestion des Photos (Dossier '{IMG_FOLDER}')...")
                photo_str = str(ad_data.get('Photos', '')).strip()
                
                # Dossier local des images (importé depuis config.py)
                if not os.path.exists(IMG_FOLDER):
                    try:
                        os.makedirs(IMG_FOLDER)
                        print(f"   (Dossier '{IMG_FOLDER}' créé, mettez vos photos dedans)")
                    except: pass

                if photo_str:
                    try:
                        # Supporte virgule ET point-virgule
                        filenames = [n.strip() for n in photo_str.replace(';', ',').split(',') if n.strip()]
                        final_photos_to_upload = []
                        
                        for fname in filenames:
                            # On cherche dans le dossier img
                            full_path = os.path.abspath(os.path.join(IMG_FOLDER, fname))
                            if os.path.exists(full_path):
                                final_photos_to_upload.append(full_path)
                            else:
                                print(f"   x Photo introuvable dans '{IMG_FOLDER}': {fname}")

                        # Fallback Intelligent : Si pas de photo spécifiée, on cherche une image avec le TITRE de l'annonce
                        if not final_photos_to_upload:
                            print("   -> Pas de fichier spécifique indiqué. Recherche par TITRE...")
                            title_clean = str(ad_data.get('Titre', '')).strip()
                            # Enlever les caractères invalides pour un fichier (slash, etc)
                            safe_title = "".join([c for c in title_clean if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
                            
                            # On cherche jpg, png, jpeg
                            for ext in ['jpg', 'png', 'jpeg', 'JPG', 'PNG']:
                                guess_path = os.path.abspath(os.path.join(IMG_FOLDER, f"{safe_title}.{ext}"))
                                if os.path.exists(guess_path):
                                    print(f"      -> Image trouvée par titre : {safe_title}.{ext}")
                                    final_photos_to_upload.append(guess_path)
                                    break # On en prend une seule pour l'instant

                        if final_photos_to_upload:
                            print(f"   -> {len(final_photos_to_upload)} photo(s) trouvée(s).")
                            
                            # Pause "Humaine" avant d'ouvrir la fenêtre de fichiers
                            self.random_sleep(2, 4)
                            
                            # Upload
                            file_input = page.locator("input[type='file']").first
                            file_input.set_input_files(final_photos_to_upload)
                            print("   -> Envoi des fichiers au navigateur...")
                            
                            # Pause "Upload" + "Vérification visuelle humaine"
                            # Important pour éviter le ban : on ne clique pas tout de suite
                            self.random_sleep(5, 8) 
                            
                            print("[Form] Validation Photos (Continuer)...")
                            cont_photo = page.get_by_role("button", name="Continuer").last
                            
                            # Pause "Hésitation" avant le clic final sur continuer
                            self.random_sleep(2, 4)
                            
                            if cont_photo.is_visible():
                                cont_photo.click()
                                self.random_sleep(1, 2)
                        else:
                            print("   -> Aucune photo valide trouvée dans 'img'.")
                            self.random_sleep(2, 3)
                            pass_btn = page.get_by_role("button", name="Continuer").or_(page.get_by_text("Continuer sans photo")).first
                            if pass_btn.is_visible(): pass_btn.click()

                    except Exception as e:
                         print(f"   !!! Erreur Photos : {e}")
                else:
                    print("   -> Colonne Photos vide. On tente de passer.")
                    self.random_sleep(1, 2)
                    try:
                         pass_btn = page.get_by_role("button", name="Continuer").first
                         if pass_btn.is_visible(): pass_btn.click()
                    except: pass
                
                # --- ATTRIBUTS DYNAMIQUES (État, Marque, Taille...) ---
                self.random_sleep(2, 3)
                print("[Form] Gestion des Attributs (Marque, État, etc.)...")
                
                # Liste des clés standards à IGNORER (car déjà gérées ou pas des attributs)
                # Ajout de variantes avec espaces pour gérer les erreurs de nommage dans le Sheet
                STANDARD_KEYS = ['ID', 'Titre', 'Description', 'Prix', 'Prix ', 'Categorie', 'Photos', 'Statut', 'Ville', 'Ville ']
                
                # On parcourt toutes les colonnes du Sheet
                for key, value in ad_data.items():
                    if key in STANDARD_KEYS: continue # On ignore les colonnes de base
                    if not value: continue # On ignore les cellules vides
                    
                    val_str = str(value).strip()
                    if not val_str: continue

                    print(f"   -> Traitement attribut : '{key}' = '{val_str}'")
                    try:
                        # 1. Trouver le Label (Sensible à la casse ou Capitalized)
                        # Ex: Colonne "type" -> Label "Type"
                        # On essaie la clé telle quelle, puis Capitalized
                        lbl = page.locator("label").filter(has_text=key).first
                        if not lbl.is_visible():
                             lbl = page.locator("label").filter(has_text=key.capitalize()).first
                        
                        if lbl.is_visible():
                            print(f"      - Label '{key}' trouvé.")
                            
                            # Clic sur le label pour activer le champ
                            lbl.click()
                            self.random_sleep(1.0, 2.0) # Augmenté pour réalisme
                            
                            # Stratégie Dropdown : Taper + Entrée
                            # D'abord on vérifie si on peut taper
                            try:
                                # On tape doucement
                                page.keyboard.type(val_str, delay=100)
                                self.random_sleep(2, 4) # Pause réflexion avant validation
                                
                                # On regarde si le texte tapé apparait comme option sélectionnable
                                opt = page.locator("div[role='option']").filter(has_text=val_str).last
                                if opt.is_visible():
                                    print(f"      - Option '{val_str}' détectée. Clic.")
                                    opt.click()
                                else:
                                    # Sinon Entrée aveugle
                                    print("      - Tentative validation (Entrée)...")
                                    page.keyboard.press("Enter")
                            except: pass

                        else:
                            # Fallback : Placeholder
                            inp = page.get_by_placeholder(key).or_(page.get_by_placeholder(key.capitalize())).first
                            if inp.is_visible():
                                inp.fill(val_str)
                            else:
                                print(f"      - Champ '{key}' absent de la page (Ignoré, normal pour certaines catégories).")

                    except Exception as e:
                        print(f"      x Erreur remplissage '{key}': {e}")
                
                 # Validation Attributs (Continuer)
                print("[Form] Validation Attributs...")
                try:
                    cont_attr = page.get_by_role("button", name="Continuer").last
                    if cont_attr.is_visible():
                        cont_attr.click()
                        self.random_sleep(1, 2)
                except: pass

                # --- DESCRIPTION ---
                self.random_sleep(2, 3)
                print("[Form] Gestion Description...")
                desc = str(ad_data.get('Description', '')).strip()
                if desc:
                    try:
                        # On cherche le textarea
                        # Souvent name="body" ou label "Description de l'annonce"
                        print("   -> Remplissage description...")
                        
                        # Essai 1 : Label
                        lbl_desc = page.get_by_label("Description de l'annonce")
                        lbl_desc.click()
                        self.random_sleep(1, 2)
                        
                        # Human Typing pour la description (RALENTI)
                        for char in desc:
                             page.keyboard.type(char)
                             time.sleep(random.uniform(0.05, 0.15)) # 50-150ms par caractère
                        
                        print("   -> Description remplie.")
                        
                        # Clic Continuer
                        print("[Form] Validation Description...")
                        cont_desc = page.get_by_role("button", name="Continuer").last
                        self.random_sleep(1, 2)
                        cont_desc.click()
                    except Exception as e:
                        # Fallback générique textarea
                        try:
                            page.locator("textarea").first.fill(desc)
                            print("   -> Description remplie (fallback).")
                            page.get_by_role("button", name="Continuer").last.click()
                        except:
                            print(f"      x Erreur Description : {e}")
                else:
                    print("   -> Description vide dans le Sheet ! (Attention champ obligatoire)")

                # --- PRIX ---
                self.random_sleep(2, 3)
                print("[Form] Gestion Prix...")
                # Récupération robuste (Prix ou Prix avec espace)
                raw_price = str(ad_data.get('Prix', '')).strip()
                if not raw_price:
                    raw_price = str(ad_data.get('Prix ', '')).strip()  # Avec espace
                
                # On garde que les chiffres (et virgule/point si besoin, mais LBC aime les entiers souvent)
                price_val = "".join([c for c in raw_price if c.isdigit()])
                
                if price_val:
                    try:
                        print(f"   -> Prix trouvé : {price_val}€")
                        # Input souvent name="price"
                        # Ou Label "Prix"
                        price_input = page.locator("input[name='price']").first
                        if not price_input.is_visible():
                             price_input = page.get_by_label("Prix", exact=False).first
                        
                        if price_input.is_visible():
                            price_input.click()
                            self.random_sleep(0.5, 1.0)
                            # Human Type
                            for char in price_val:
                                page.keyboard.type(char)
                                time.sleep(random.uniform(0.05, 0.15))
                            
                            self.random_sleep(1, 2)
                            print("   -> Prix rempli.")
                            
                            # Clic Continuer
                            print("[Form] Validation Prix (avec délai)...")
                            self.random_sleep(2, 4) # Délai demandé
                            page.get_by_role("button", name="Continuer").last.click()
                        else:
                            print("   x Input Prix introuvable.")
                    except Exception as e:
                         print(f"   !!! Erreur Prix : {e}")
                else:
                    print("   -> Colonne Prix vide ou non numérique (Pas grave si c'est 'Sur Devis').")
                    # Parfois on peut continuer sans prix ? Souvent obligatoire.
                    # On tente de continuer au cas où
                    try:
                         page.get_by_role("button", name="Continuer").last.click()
                    except: pass
                
                # --- VILLE / LOCALISATION ---
                self.random_sleep(2, 3)
                print("[Form] Gestion Ville...")
                # Récupération robuste (Ville ou Ville + espace)
                city = str(ad_data.get('Ville', '')).strip()
                if not city: city = str(ad_data.get('Ville ', '')).strip()

                if city:
                    try:
                        # Input souvent location_input
                        print(f"   -> Recherche Ville : {city}")
                        
                        # Stratégie ciblée sur le screenshot (Placeholder exact)
                        loc_input = page.get_by_placeholder("Renseignez votre adresse ou votre ville")
                        
                        if not loc_input.is_visible():
                             # Fallback Label
                             loc_input = page.get_by_label("Adresse", exact=False).first
                        
                        if loc_input.is_visible():
                            loc_input.click()
                            self.random_sleep(0.5, 1.0)
                            
                            # On vide le champ si besoin (parfois pré-rempli)
                            loc_input.clear()
                            
                            # Typing
                            for char in city:
                                page.keyboard.type(char)
                                time.sleep(random.uniform(0.05, 0.15))
                            
                            print("   -> Attente suggestions...")
                            self.random_sleep(2, 4) # Attente suggestions
                            
                            # Sélectionner la première suggestion: role="option" ou class*="LocationSuggestion"
                            # Souvent c'est une liste ul/li ou div
                            first_opt = page.locator("li[role='option'], div[role='option']").first
                            
                            if first_opt.is_visible():
                                print("   -> Clic première suggestion Ville.")
                                first_opt.click()
                                self.random_sleep(1, 2)
                            else:
                                print("   x Aucune suggestion de ville apparue (Essayez d'appuyer sur Entrée).")
                                page.keyboard.press("Enter")
                                self.random_sleep(1, 2)
                            
                            # Valider avec le bouton "Continuer" - Recherche robuste
                            print("[Form] Validation Ville - Recherche bouton 'Continuer'...")
                            self.random_sleep(1, 2)
                            
                            # Stratégie 1 : Par rôle (méthode principale)
                            continue_btn = None
                            try:
                                continue_btn = page.get_by_role("button", name="Continuer").last
                                if continue_btn.is_visible(timeout=3000):
                                    print("   -> Bouton 'Continuer' trouvé (par rôle). Clic...")
                                    continue_btn.click()
                                    self.random_sleep(2, 3)  # Attente chargement page suivante
                                    page.wait_for_load_state("domcontentloaded")
                                    print("   -> Page suivante chargée après validation ville.")
                                else:
                                    continue_btn = None
                            except Exception as e1:
                                print(f"   -> Tentative 1 échouée: {e1}")
                                continue_btn = None
                            
                            # Stratégie 2 : Par texte visible (fallback)
                            if not continue_btn:
                                try:
                                    continue_btn = page.locator("button").filter(has_text="Continuer").last
                                    if continue_btn.is_visible(timeout=2000):
                                        print("   -> Bouton 'Continuer' trouvé (par texte). Clic...")
                                        continue_btn.click()
                                        self.random_sleep(2, 3)
                                        page.wait_for_load_state("domcontentloaded")
                                        print("   -> Page suivante chargée.")
                                    else:
                                        continue_btn = None
                                except Exception as e2:
                                    print(f"   -> Tentative 2 échouée: {e2}")
                                    continue_btn = None
                            
                            # Stratégie 3 : Sélecteur générique (dernier recours)
                            if not continue_btn:
                                try:
                                    continue_btn = page.locator("button[type='submit']").last
                                    if continue_btn.is_visible(timeout=2000):
                                        print("   -> Bouton submit trouvé. Clic...")
                                        continue_btn.click()
                                        self.random_sleep(2, 3)
                                        page.wait_for_load_state("domcontentloaded")
                                    else:
                                        continue_btn = None
                                except:
                                    pass
                            
                            # Si aucune stratégie n'a fonctionné, essayer Entrée
                            if not continue_btn:
                                print("   ⚠️ Bouton 'Continuer' non trouvé. Essai avec Entrée...")
                                page.keyboard.press("Enter")
                                self.random_sleep(2, 3)
                                page.wait_for_load_state("domcontentloaded")
                                print("   -> Tentative validation avec Entrée.")
                        else:
                            print("   x Champ Ville (Adresse) introuvable.")
                            # Essayer quand même de continuer
                            try:
                                continue_btn = page.get_by_role("button", name="Continuer").last
                                if continue_btn.is_visible(timeout=2000):
                                    continue_btn.click()
                                    self.random_sleep(2, 3)
                                    page.wait_for_load_state("domcontentloaded")
                            except:
                                pass
                    except Exception as e:
                        print(f"      x Erreur Ville : {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("   -> Colonne Ville vide ! Cela risque de bloquer.")
                    try:
                         continue_btn = page.get_by_role("button", name="Continuer").last
                         if continue_btn.is_visible(timeout=2000):
                             continue_btn.click()
                             self.random_sleep(2, 3)
                             page.wait_for_load_state("domcontentloaded")
                    except: pass
                
                # --- VALIDATION FINALE (DÉPÔT) ---
                # Cette section s'exécute TOUJOURS après la gestion de la ville
                if filled:
                    self.random_sleep(3, 5)
                    print("[Final] Recherche bouton pour validation finale (Continuer/Déposer)...")
                    
                    # Attendre que la page soit complètement chargée
                    try:
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except:
                        page.wait_for_load_state("domcontentloaded")
                    
                    # Vérification captcha avant validation finale
                    captcha_handler = CaptchaHandler()
                    if not captcha_handler.check_at_key_moments(page, "avant validation finale"):
                        print("[Final] ❌ Échec résolution captcha avant validation")
                        result = "CAPTCHA_FAILED_BEFORE_SUBMIT"
                    else:
                        # Recherche robuste du bouton final (peut être "Continuer" ou "Déposer l'annonce")
                        final_btn = None
                        
                        # Stratégie 1 : Chercher "Continuer" d'abord (souvent le cas)
                        try:
                            final_btn = page.get_by_role("button", name="Continuer").last
                            if final_btn.is_visible(timeout=3000):
                                print("   -> Bouton 'Continuer' trouvé pour validation finale.")
                            else:
                                final_btn = None
                        except:
                            final_btn = None
                        
                        # Stratégie 2 : Chercher "Déposer l'annonce"
                        if not final_btn:
                            try:
                                final_btn = page.get_by_role("button", name="Déposer l'annonce").first
                                if final_btn.is_visible(timeout=2000):
                                    print("   -> Bouton 'Déposer l'annonce' trouvé.")
                                else:
                                    final_btn = None
                            except:
                                final_btn = None
                        
                        # Stratégie 3 : Chercher "Valider" ou "Publier"
                        if not final_btn:
                            try:
                                final_btn = page.get_by_role("button", name="Valider").first
                                if not final_btn.is_visible(timeout=2000):
                                    final_btn = page.get_by_role("button", name="Publier").first
                                    if not final_btn.is_visible(timeout=2000):
                                        final_btn = None
                            except:
                                final_btn = None
                        
                        # Stratégie 4 : Recherche par texte (fallback)
                        if not final_btn:
                            try:
                                all_buttons = page.locator("button").all()
                                for btn in all_buttons:
                                    try:
                                        text = btn.inner_text().lower()
                                        if "continuer" in text or "déposer" in text or "publier" in text or "valider" in text:
                                            if btn.is_visible():
                                                final_btn = btn
                                                print(f"   -> Bouton trouvé par recherche générique: '{btn.inner_text()}'")
                                                break
                                    except:
                                        continue
                            except:
                                pass
                        
                        if final_btn and final_btn.is_visible():
                            btn_text = ""
                            try:
                                btn_text = final_btn.inner_text()
                            except:
                                btn_text = "inconnu"
                            
                            print(f">>> [READY] Bouton de validation finale détecté: '{btn_text}'")
                            
                            if ENABLE_REAL_POSTING:
                                # MODE PRODUCTION : On publie vraiment
                                print(f">>> 🚀 PUBLICATION RÉELLE - Clic sur '{btn_text}'...")
                                self.random_sleep(2, 4)  # Hésitation humaine finale
                                final_btn.click()
                                print(">>> ✅ Clic effectué ! Attente page de boost...")
                                
                                # Attendre que la page de boost se charge
                                try:
                                    page.wait_for_load_state("domcontentloaded", timeout=15000)
                                    self.random_sleep(3, 5)  # Laisser le temps à la page de se charger complètement
                                    
                                    print("[Boost] Recherche bouton 'Déposer sans booster'...")
                                    
                                    # Chercher le bouton pour déposer sans boost
                                    # Plusieurs formulations possibles
                                    no_boost_btn = None
                                    
                                    # Stratégie 1 : Texte exact
                                    try:
                                        no_boost_btn = page.get_by_role("button", name="Déposer sans booster mon annonce").first
                                        if no_boost_btn.is_visible(timeout=3000):
                                            print("   -> Bouton trouvé (stratégie 1)")
                                        else:
                                            no_boost_btn = None
                                    except:
                                        no_boost_btn = None
                                    
                                    # Stratégie 2 : Recherche par texte partiel
                                    if not no_boost_btn:
                                        try:
                                            no_boost_btn = page.locator("button").filter(has_text="sans booster").first
                                            if no_boost_btn.is_visible(timeout=2000):
                                                print("   -> Bouton trouvé (stratégie 2)")
                                            else:
                                                no_boost_btn = None
                                        except:
                                            no_boost_btn = None
                                    
                                    # Stratégie 3 : Recherche générique dans tous les boutons
                                    if not no_boost_btn:
                                        try:
                                            all_buttons = page.locator("button").all()
                                            for btn in all_buttons:
                                                try:
                                                    text = btn.inner_text().lower()
                                                    if "sans booster" in text or "déposer sans" in text:
                                                        if btn.is_visible():
                                                            no_boost_btn = btn
                                                            print(f"   -> Bouton trouvé (stratégie 3): '{btn.inner_text()}'")
                                                            break
                                                except:
                                                    continue
                                        except:
                                            pass
                                    
                                    if no_boost_btn and no_boost_btn.is_visible():
                                        print(">>> 🎯 Clic sur 'Déposer sans booster mon annonce'...")
                                        self.random_sleep(2, 3)  # Hésitation réaliste
                                        no_boost_btn.click()
                                        print(">>> ✅ Clic effectué ! Attente confirmation finale...")
                                        
                                        # Attendre la page de confirmation
                                        try:
                                            page.wait_for_load_state("domcontentloaded", timeout=15000)
                                            self.random_sleep(5, 8)
                                            
                                            # Vérifier les messages de confirmation
                                            page_content = page.content().lower()
                                            if any(text in page_content for text in [
                                                "votre annonce a été déposée",
                                                "annonce déposée",
                                                "votre annonce est en ligne",
                                                "merci pour votre annonce",
                                                "en cours de vérification"
                                            ]):
                                                print(">>> ✅ Annonce publiée avec succès !")
                                                result = "SUCCESS_PUBLISHED"
                                            else:
                                                print("   ⚠️ Confirmation incertaine, mais clic effectué")
                                                result = "SUCCESS_PUBLISHED_PENDING"
                                        except:
                                            print("   ⚠️ Timeout confirmation, mais clic effectué")
                                            result = "SUCCESS_PUBLISHED_UNCONFIRMED"
                                    else:
                                        print("   ❌ Bouton 'Déposer sans booster' introuvable")
                                        print("   -> Peut-être déjà sur la page finale ?")
                                        self.random_sleep(5, 8)
                                        result = "SUCCESS_PUBLISHED_NO_BOOST_BTN"
                                        
                                except Exception as e:
                                    print(f"   ⚠️ Erreur page de boost : {e}")
                                    self.random_sleep(5, 8)
                                    result = "SUCCESS_PUBLISHED_BOOST_ERROR"
                            else:
                                # MODE TEST : On simule (pas de vrai clic)
                                print(f">>> 🧪 MODE TEST - Simulation du clic sur '{btn_text}' (ENABLE_REAL_POSTING=False)")
                                print(">>> Pour activer la vraie publication, mettez ENABLE_REAL_POSTING=True")
                                self.random_sleep(2, 3)  # Simulation réaliste
                                result = "SUCCESS_SIMULATED"
                        else: 
                            print("   x Bouton de validation finale introuvable.")
                            print("   -> Vérification de l'URL actuelle...")
                            print(f"   -> URL: {page.url}")
                            print("   -> Tentative de capture d'écran pour debug...")
                            try:
                                screenshot_path = f"debug_screenshot_{int(time.time())}.png"
                                page.screenshot(path=screenshot_path)
                                print(f"   -> Screenshot sauvegardé: {screenshot_path}")
                            except Exception as e:
                                print(f"   -> Erreur screenshot: {e}")
                            result = "FAILURE_FINAL_BUTTON_NOT_FOUND"
                        
                        # Pause observation après publication
                        if result.startswith("SUCCESS"):
                            print("[Cleanup] Pause observation (15s)...")
                            self.random_sleep(15, 20)  # Observer le résultat
                else:
                    print(">>> ECHEC : Champ titre introuvable.")
                    result = "FAILURE_FORM_NOT_FOUND"
                
            except StopBotException:
                print("[Bot] ⏹ Arrêt demandé - Fermeture immédiate du navigateur.")
                result = "STOPPED_BY_USER"
                
            except TargetClosedError as e:
                print("[Browser] ⚠️ Le navigateur a été fermé manuellement.")
                print("   -> Le bot s'arrête proprement.")
                self.log("⚠️ Navigateur fermé manuellement - Arrêt du bot", 'warning')
                result = "BROWSER_CLOSED_MANUALLY"
                
            finally:
                print("[Cleanup] Fermeture du navigateur...")
                try:
                    browser.close()
                except:
                    pass
            
            return result

    def download_photos(self, urls):
        """Télécharge les photos dans un dossier temp et retourne les chemins absolus."""
        import requests
        folder = "temp_images"
        if not os.path.exists(folder): os.makedirs(folder)
        
        local_paths = []
        for i, url in enumerate(urls[:3]): # Max 3 photos pour le test
            try:
                print(f"      - Downloading: {url} ...")
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    ext = "jpg"
                    if "png" in url.lower(): ext = "png"
                    filename = f"{folder}/photo_{i}.{ext}"
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    local_paths.append(os.path.abspath(filename))
            except Exception as e:
                print(f"      x Erreur download {url}: {e}")
        return local_paths
