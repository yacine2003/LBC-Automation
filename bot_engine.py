

import time
import random
import os
import sys
import base64
from playwright.sync_api import sync_playwright

import gsheet_manager

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
EMAIL = "comptleboncoin@outlook.fr"
PASSWORD = "Compte123@GED5"

LOGIN_URL = "https://www.leboncoin.fr/se-connecter"
POST_AD_URL = "https://www.leboncoin.fr/deposer-une-annonce"
COOKIE_FILE = "state.json"

class LBCPoster:
    def __init__(self):
        self.sheet_name = "LBC-Automation" 

    def random_sleep(self, min_s=2.0, max_s=5.0):
        """Pause aléatoire"""
        duration = random.uniform(min_s, max_s)
        print(f"   [Sleep] Pause de {duration:.2f}s...")
        time.sleep(duration)

    def capture_screenshot(self, page):
        """Capture screenshot et encode en base64 pour streaming"""
        try:
            screenshot_bytes = page.screenshot()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return screenshot_base64
        except Exception as e:
            print(f"   ! Erreur capture screenshot : {e}")
            return None

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
                print("   -> 'Accepter & Fermer'.")
                self.random_sleep(1, 2)
                accept_btn.click()
                return True
            elif accept_btn_alt.is_visible(timeout=1000):
                 print("   -> 'Tout accepter'.")
                 self.random_sleep(1, 2)
                 accept_btn_alt.click()
                 return True
            return False
        except:
            return False

    def perform_login(self, page):
        """Flux de login complet"""
        print("--- LOGIN FLOW ---")
        page.wait_for_load_state("domcontentloaded")
        self.random_sleep(2, 3)
        self.handle_cookies(page)

        # 1. Email
        print("   -> Email...")
        try:
            email_sel = "input[name='email']"
            page.wait_for_selector(email_sel, timeout=5000)
            self.human_type(page, email_sel, EMAIL, 0.08, 0.25)
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
            self.human_type(page, pass_sel, PASSWORD, 0.08, 0.25)
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
        Point d'entrée principal (remplace le main de prototype.py)
        
        Args:
            streaming_callback: Fonction async appelée avec les screenshots (optionnel)
                               Signature: async callback(screenshot_base64, status_message)
        """
        print(">>> Lancement Processus Automatisé (via API) <<<")
        
        # 1. Lecture Sheet
        try:
            sheet = gsheet_manager.connect_to_sheets(self.sheet_name)
            ad_data, row_num = gsheet_manager.get_next_ad_to_publish(sheet)
            if not ad_data:
                print(">>> STOP : Rien à faire.")
                return "NO_AD_FOUND"
            print(f">>> Annonce trouvée : {ad_data.get('Titre')}")
        except Exception as e:
            print(f"!!! Erreur Sheet: {e}")
            return f"ERROR_SHEET_{e}"

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

            if os.path.exists(COOKIE_FILE):
                context = browser.new_context(storage_state=COOKIE_FILE, **context_args)
            else:
                context = browser.new_context(**context_args)

            try:
                from playwright_stealth import stealth_sync
                page = context.new_page()
                stealth_sync(page)
            except:
                page = context.new_page()

            # Navigation
            print(f"[Nav] Vers {POST_AD_URL}")
            page.goto(POST_AD_URL)
            page.wait_for_load_state("domcontentloaded")
            self.random_sleep(2, 4)
            self.handle_cookies(page)

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
                    # On attend un peu que le header charge
                    btn = page.locator("button, a").filter(has_text="Me connecter").first
                    btn.wait_for(state="visible", timeout=3000)
                    btn.click()
                    
                    self.perform_login(page)
                    context.storage_state(path=COOKIE_FILE) # Save session

                    print("[Nav] Retour Dépôt...")
                    page.wait_for_load_state("domcontentloaded")
                    self.random_sleep(2, 3)
                except:
                    print("Could not click login button or login failed. Continuing anyway...")
                if "deposer" not in page.url: page.goto(POST_AD_URL)

            # Remplissage
            self.random_sleep(1, 2)
            print("[Form] Remplissage Titre...")
            
            filled = False
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
                print("[Form] Gestion des Photos (Dossier 'img')...")
                photo_str = str(ad_data.get('Photos', '')).strip()
                
                # Dossier local des images
                IMG_FOLDER = "img"
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
                # Liste des clés standards à IGNORER (car déjà gérées ou pas des attributs)
                # Ajout de 'Ville' et 'Ville ' pour éviter le traitement générique
                STANDARD_KEYS = ['ID', 'Titre', 'Description', 'Prix', 'Categorie', 'Photos', 'Statut', 'Ville', 'Ville ']
                
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
                raw_price = str(ad_data.get('Prix', '')).strip()
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
                # Récupératon robuste (Ville ou Ville + espace)
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
                            
                            # Valider
                            print("[Form] Validation Ville...")
                            self.random_sleep(1, 2)
                            page.get_by_role("button", name="Continuer").last.click()
                        else:
                            print("   x Champ Ville (Adresse) introuvable.")
                    except Exception as e:
                        print(f"      x Erreur Ville : {e}")
                else:
                    print("   -> Colonne Ville vide ! Cela risque de bloquer.")
                    try:
                         page.get_by_role("button", name="Continuer").last.click()
                    except: pass
                
                # --- VALIDATION FINALE (DÉPÔT) ---
                self.random_sleep(3, 5)
                print("[Final] Recherche bouton 'Déposer l'annonce'...")
                
                # Checkbox CGV ? Souvent implicite ou absent maintenant.
                
                # Bouton Déposer
                # "Déposer mon annonce" ou "Valider"
                deposit_btn = page.get_by_role("button", name="Déposer l'annonce").or_(page.get_by_role("button", name="Valider"))
                
                # --- MODE TEST : ON NE CLIQUE PAS VRAIMENT POUR L'INSTANT ---
                # Pour éviter le spam pendant le dev.
                # Décommenter la ligne ci-dessous pour activer le vrai dépôt.
                # if deposit_btn.is_visible():
                #     print(">>> [TEST MODE] Bouton trouvé ! Je ne clique pas pour ne pas payer/publier pour rien.")
                #     # deposit_btn.click() 
                #     result = "SUCCESS_SIMULATED"
                # else:
                #     print("   x Bouton final non trouvé.")
                
                if deposit_btn.is_visible():
                     print(">>> [READY] Bouton 'Déposer' détecté. En attente de votre feu vert pour activer le clic.")
                     result = "SUCCESS_READY_TO_POST"
                else: 
                     result = "SUCCESS_NO_BUTTON"
                
                # result = "SUCCESS"
            else:
                print(">>> ECHEC : Champ titre introuvable.")
                result = "FAILURE_FORM_NOT_FOUND"

            print("[Cleanup] Pause puis fermeture (60s)...")
            time.sleep(60) # Pause longue pour vérification visuelle
            browser.close()
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
