"""
Launcher pour LBC Automation
Point d'entrée pour la compilation en .exe avec PyInstaller
"""

import sys
import os
import subprocess
import webbrowser
import time
from pathlib import Path

def get_base_path():
    """Retourne le chemin du dossier de l'exe ou du script"""
    if getattr(sys, 'frozen', False):
        # Mode exe (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Mode script normal
        return Path(__file__).parent

def setup_playwright_path():
    """Configure le chemin permanent pour les navigateurs Playwright"""
    # Utiliser un dossier dans AppData pour stocker les navigateurs
    if os.name == 'nt':  # Windows
        browsers_path = Path(os.environ.get('LOCALAPPDATA')) / 'LBC_Automation' / 'playwright_browsers'
    else:  # macOS/Linux
        browsers_path = Path.home() / '.lbc_automation' / 'playwright_browsers'
    
    browsers_path.mkdir(parents=True, exist_ok=True)
    
    # Définir la variable d'environnement pour Playwright
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browsers_path)
    
    return browsers_path

def check_chromium():
    """Vérifie si Chromium est installé, sinon l'installe"""
    try:
        from playwright.sync_api import sync_playwright
        print("⏳ Vérification de Chromium...")
        
        try:
            with sync_playwright() as p:
                # Test simple de lancement
                browser = p.chromium.launch(headless=True)
                browser.close()
            print("✅ Chromium installé et fonctionnel")
            return True
        except Exception as e:
            print(f"⚠️  Chromium non installé ou incomplet : {e}")
            return False
    except ImportError:
        print("❌ Playwright non installé")
        return False

def install_chromium():
    """Installe Chromium pour Playwright"""
    print("\n" + "=" * 60)
    print("📥 INSTALLATION DE CHROMIUM")
    print("=" * 60)
    print("Chromium est nécessaire pour l'automatisation du navigateur.")
    print("Installation en cours (cela peut prendre quelques minutes)...")
    print()
    
    try:
        # Utiliser l'API Playwright directement pour installer les navigateurs
        from playwright._impl._driver import compute_driver_executable, get_driver_env
        
        driver_executable = compute_driver_executable()
        env = get_driver_env()
        
        # Ajouter le chemin des navigateurs à l'environnement
        env.update(os.environ.copy())
        
        result = subprocess.run(
            [str(driver_executable), "install", "chromium"],
            env=env,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✅ Chromium installé avec succès !")
            return True
        else:
            print(f"\n❌ Erreur lors de l'installation (code {result.returncode})")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False

def open_browser_delayed():
    """Ouvre le navigateur après un délai"""
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:8000")
        print("🌐 Navigateur ouvert sur http://localhost:8000")
    except Exception as e:
        print(f"⚠️  Impossible d'ouvrir le navigateur : {e}")
        print("   Ouvrez manuellement : http://localhost:8000")

def main():
    """Point d'entrée principal"""
    BASE_PATH = get_base_path()
    os.chdir(BASE_PATH)
    
    # Configurer le chemin permanent pour Playwright
    browsers_path = setup_playwright_path()
    
    # Bannière
    print("\n" + "=" * 60)
    print("🤖 LBC AUTOMATION - Automatisation LeBonCoin")
    print("=" * 60)
    print(f"📁 Dossier d'installation : {BASE_PATH}")
    print(f"📦 Navigateurs Playwright : {browsers_path}")
    print()
    
    # Vérifier et installer Chromium si nécessaire
    if not check_chromium():
        print("\n⚠️  Première installation détectée")
        if not install_chromium():
            print("\n❌ L'installation de Chromium a échoué.")
            print("   Le bot ne pourra pas fonctionner sans Chromium.")
            input("\nAppuyez sur Entrée pour quitter...")
            sys.exit(1)
    
    # Ouvrir le navigateur en arrière-plan
    import threading
    browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
    browser_thread.start()
    
    # Lancer le serveur
    print("\n" + "=" * 60)
    print("🚀 DÉMARRAGE DU SERVEUR WEB")
    print("=" * 60)
    print("Interface disponible sur : http://localhost:8000")
    print("Appuyez sur Ctrl+C pour arrêter")
    print()
    
    try:
        from main import app
        import uvicorn
        
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n⏹  Arrêt du serveur...")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage : {e}")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)

if __name__ == "__main__":
    main()
