import os
import sys
import webbrowser
import threading
import uvicorn
import time
import requests
from pathlib import Path
import logging

# Configuration du logging
# On redirige stdout et stderr vers un fichier pour le debug en mode "noconsole"
log_file = Path("app.log")
logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Fonction pour rediriger stdout/stderr vers le logger
class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

# Redirection si on est en mode "frozen" (exécutable)
if getattr(sys, 'frozen', False):
    sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
    sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)

def open_browser(url):
    """Ouvre le navigateur par défaut après une courte pause"""
    time.sleep(1.5)  # Attendre que le serveur démarre
    try:
        logging.info(f"Opening browser at {url}")
        webbrowser.open(url)
    except Exception as e:
        logging.error(f"Failed to open browser: {e}")

def check_playwright_browsers():
    """Vérifie si les navigateurs Playwright sont installés"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Tente de lancer chromium pour voir s'il est là
            try:
                browser = p.chromium.launch()
                browser.close()
                logging.info("Playwright browsers found.")
                return True
            except Exception as e:
                logging.warning(f"Playwright browsers check failed: {e}")
                return False
    except Exception as e:
        logging.error(f"Playwright check error: {e}")
        return False

def install_browsers():
    """Tente d'installer les navigateurs"""
    logging.info("Attempting to install Playwright browsers...")
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        logging.info("Browsers installed successfully.")
    except Exception as e:
        logging.error(f"Failed to install browsers: {e}")

def main():
    logging.info("Application starting...")
    
    # Vérification des navigateurs (optionnel, peut être lourd au démarrage)
    # On le fait uniquement si on n'arrive pas à lancer un browser plus tard, 
    # mais ici on assume que le user a suivi l'install ou que c'est le premier run.
    # Pour l'instant on log juste.
    
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    
    # Lancer le navigateur dans un thread séparé
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    
    # Démarrer le serveur Uvicorn
    # Important: on importe app ici pour éviter des effets de bord avant le setup du logging
    try:
        # On doit ajouter le dossier courant au path pour que les imports de main.py fonctionnent
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # FIX: On passe log_config=None pour empêcher Uvicorn de chercher ses fichiers de config par défaut
        # (ce qui plante dans un .exe). Uvicorn utilisera alors le logging standard qu'on a configuré plus haut.
        
        logging.info(f"Starting server on {url}")
        uvicorn.run("main:app", host=host, port=port, reload=False, workers=1, log_config=None)
        
    except Exception as e:
        logging.critical(f"Server crashed: {e}")
        # En cas de crash fatal, on essaie d'afficher une popup si possible (sur Windows)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"Erreur fatale: {str(e)}", "Erreur LBC Automation", 0x10)
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
