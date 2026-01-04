
import time
import random
import os
import sys
from playwright.sync_api import sync_playwright

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
EMAIL = "comptleboncoin@outlook.fr"
PASSWORD = "Compte123@GED5"

LOGIN_URL = "https://www.leboncoin.fr/se-connecter"
POST_AD_URL = "https://www.leboncoin.fr/deposer-une-annonce"
COOKIE_FILE = "state.json"

# -----------------------------------------------------------------------------
# FONCTIONS "HUMAINES"
# -----------------------------------------------------------------------------

def random_sleep(min_s=2.0, max_s=5.0):
    """Pause aléatoire pour simuler un comportement humain."""
    duration = random.uniform(min_s, max_s)
    print(f"   [Sleep] Pause de {duration:.2f}s...")
    time.sleep(duration)

def human_type(page, selector, text, delay_min=0.1, delay_max=0.3):
    """Frappe au clavier caractère par caractère avec délai variable (Plus lent)."""
    print(f"   [Typing] Écriture '{text}' dans {selector}...")
    try:
        element = page.locator(selector).first
        if not element.is_visible():
            print(f"   !!! Élément {selector} introuvable pour écriture.")
            return

        element.click() # Focus
        # Petite pause avant de commencer à écrire
        random_sleep(0.5, 1.0)
        
        for char in text:
            page.keyboard.type(char)
            # Délai entre chaque touche (plus lent)
            time.sleep(random.uniform(delay_min, delay_max))
        

        random_sleep(0.5, 1.5)
    except Exception as e:
        print(f"   !!! Erreur de frappe : {e}")

def handle_cookies(page):
    """Gère la bannière de cookies spécifique Leboncoin."""
    print("   -> Vérification de la bannière Cookies...")
    try:
        # Sélecteur basé sur le screenshot : "Accepter & Fermer"
        # On attend un peu que ça apparaisse
        accept_btn = page.get_by_role("button", name="Accepter & Fermer")
        
        # Parfois c'est juste "Tout accepter"
        accept_btn_alt = page.get_by_role("button", name="Tout accepter")

        if accept_btn.is_visible(timeout=3000):
            print("   -> Bannière détectée (Accepter & Fermer).")
            random_sleep(1, 2) # Petite hésitation humaine
            accept_btn.click()
            print("   -> Cookies acceptés.")
            return True
        elif accept_btn_alt.is_visible(timeout=1000):
             print("   -> Bannière détectée (Tout accepter).")
             random_sleep(1, 2)
             accept_btn_alt.click()
             print("   -> Cookies acceptés.")
             return True
        else:
            print("   -> Pas de bannière visible immédiatement.")
            return False
    except Exception as e:
        print(f"   -> Info Cookie: {e}")
        return False

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main():
    print("--- LBC AUTOMATION PROTOTYPE (V2) ---")
    
    with sync_playwright() as p:
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
        print("[1/5] Lancement de Chromium...")
        browser = p.chromium.launch(
            headless=False, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context_args = {
            "user_agent": user_agent,
            "viewport": {"width": 1280, "height": 720},
            "locale": "fr-FR"
        }
        
        # Chargement session ou nouvelle
        if os.path.exists(COOKIE_FILE):
            print(f"   -> Chargement session depuis '{COOKIE_FILE}'")
            context = browser.new_context(storage_state=COOKIE_FILE, **context_args)
        else:
            print("   -> Nouvelle session.")
            context = browser.new_context(**context_args)

        # Stealth
        try:
            from playwright_stealth import stealth_sync
            page = context.new_page()
            stealth_sync(page)
        except ImportError:
            page = context.new_page()

        # 2. Accès direct à la page de dépôt
        print(f"[2/5] Navigation vers {POST_AD_URL} ...")
        page.goto(POST_AD_URL)
        page.wait_for_load_state("domcontentloaded")
        random_sleep(2, 4)

        # Gestion Cookie immédiate si présente (souvent au premier chargement)
        handle_cookies(page)

        # 3. Détection de l'état de connexion
        # Si on est redirigé vers le login, ou si la page contient le texte de login
        login_needed = False
        
        # Cas 1 : Redirection URL
        if "connexion" in page.url or "login" in page.url:
            login_needed = True
        
        # Cas 2 : Contenu de la page (Texte "Connectez-vous")
        if not login_needed:
             # On attend un tout petit peu pour être sûr que le rendu est fini
             page.wait_for_timeout(1000)
             page_content = page.content()
             if "Connectez-vous ou créez un compte" in page_content or "Me connecter" in page_content:
                 print("   -> Texte 'Connectez-vous' détecté sur la page.")
                 login_needed = True

        if login_needed:
            print("[3/5] Connexion requise sur cette page.")
            
            # Essai de clic sur "Me connecter" présent sur la page
            connect_btn = page.locator("button, a").filter(has_text="Me connecter").first
            
            if connect_btn.is_visible():
                print("   -> Clic sur le bouton 'Me connecter' de la page...")
                connect_btn.click()
            else:
                print("   -> Bouton non trouvé, force navigation vers URL Login...")
                page.goto(LOGIN_URL)
            
            perform_login(page)
            
            # Sauvegarde après login
            print(f"   -> Sauvegarde de la session dans '{COOKIE_FILE}'")
            context.storage_state(path=COOKIE_FILE)

            # Retour page dépôt (si pas redirigé auto)
            print(f"[4/5] Retour sur {POST_AD_URL}...")
            page.wait_for_load_state("domcontentloaded")
            random_sleep(2, 3)
            # Vérif si on est revenu
            if "deposer" not in page.url:
                 page.goto(POST_AD_URL)
        else:
            print("   -> Aucune demande de connexion détectée. (Session active ?)")

        # 4. Vérification finale STRICTE
        random_sleep(2, 4)
        print("   -> Analyse de la page finale...")
        
        # On cherche un champ INPUT de type text (souvent le titre) ou le texte "Titre de l'annonce"
        is_success = False
        
        if page.get_by_text("Titre de l'annonce").is_visible() or page.locator("input[name='subject']").is_visible():
            is_success = True
        
        if is_success:
             print("\n>>> SUCCÈS : Formulaire de dépôt VRAIMENT accessible (Champ Titre trouvé) ! <<<")
        else:
             print("\n>>> ECHEC : Pas de formulaire détecté. <<<")
             print("    La page semble bloquée ou toujours en mode 'invité'.")
             print(f"    URL actuelle : {page.url}")

        print("Pause finale de 30s...")
        time.sleep(30)
        browser.close()

def perform_login(page):
    """Exécute le login (Nouveau flux multi-étape)."""
    print("--- LOGIN FLOW ---")
    page.wait_for_load_state("domcontentloaded")
    random_sleep(2, 3)
    
    # 1. Bannière Cookies
    handle_cookies(page)

    # 2. Email
    print("   -> Saisie Email...")
    try:
        email_selector = "input[name='email']"
        page.wait_for_selector(email_selector, timeout=5000)
        human_type(page, email_selector, EMAIL, delay_min=0.08, delay_max=0.25)
    except:
        print("   !!! Champ email introuvable.")
        return

    # 3. Validation Email (Bouton "Continuer")
    print("   -> Clic 'Continuer'...")
    try:
        # Le bouton s'appelle souvent "Continuer" à cette étape
        continue_btn = page.get_by_role("button", name="Continuer").first
        if continue_btn.is_visible():
            random_sleep(1, 2)
            continue_btn.click()
        else:
            # Fallback : Chercher un bouton submit générique si "Continuer" n'est pas trouvé
            submit_btn = page.locator("button[type='submit']").first
            if submit_btn.is_visible():
                 submit_btn.click()
            else:
                 print("   !!! Bouton 'Continuer' introuvable.")
    except Exception as e:
        print(f"   !!! Erreur clic Continuer: {e}")

    # 4. Password (Step 2)
    print("   -> Attente champ Password...")
    try:
        # On attend que l'animation se fasse et que le champ apparaisse
        password_selector = "input[name='password']"
        page.wait_for_selector(password_selector, timeout=10000)
        
        # Saisie Password
        human_type(page, password_selector, PASSWORD, delay_min=0.08, delay_max=0.25)
    except:
         print("   !!! Le champ Password n'est pas apparu (Blocage ? Email invalide ?).")
         return

    # 5. Validation Finale
    print("   -> Validation finale (Se connecter)...")
    try:
        # Check Cookies again (parfois ils reviennent)
        handle_cookies(page)

        login_btn = page.get_by_role("button", name="Se connecter").or_(page.locator("button[type='submit']")).first
        if login_btn.is_visible():
            random_sleep(1, 2)
            login_btn.click()
        else:
            # Parfois Entrée suffit
            page.keyboard.press("Enter")
    except Exception as e:
        print(f"   !!! Erreur clic final: {e}")
    
    # Attente post-submit
    print("   -> Attente redirection...")
    page.wait_for_timeout(5000)

if __name__ == "__main__":
    main()
    main()
