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
    """Tente d'installer les navigateurs (robuste pour version compilée)"""
    logging.info("Attempting to install Playwright browsers...")
    
    # Méthode 1: Appel direct au module (fiable pour PyInstaller)
    try:
        from playwright.__main__ import main
        import sys
        
        logging.info("Method 1: Direct Playwright module call...")
        # On sauvegarde sys.argv car main() l'utilise
        old_argv = sys.argv
        sys.argv = ["playwright", "install", "chromium"]
        
        try:
            main()
            logging.info("Browsers installed successfully via direct call.")
            return
        except SystemExit:
            # main() peut faire sys.exit(), on l'attrape
            logging.info("Playwright install finished (SystemExit caught).")
        finally:
            sys.argv = old_argv
            
    except Exception as e:
        logging.warning(f"Method 1 failed: {e}")

    # Méthode 2: Subprocess (Fallback)
    try:
        logging.info("Method 2: Subprocess call...")
        import subprocess
        # Sur Windows frozen, sys.executable est l'exe lui-même. 
        # Si ça échoue, on espère que 'playwright' est dans le PATH ou que python est accessible.
        cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
        subprocess.run(cmd, check=True)
        logging.info("Browsers installed successfully via subprocess.")
    except Exception as e:
        logging.error(f"Failed to install browsers: {e}")
        # Dernier espoir : essayer juste 'playwright' si c'est dans le PATH global
        try:
            import subprocess
            subprocess.run(["playwright", "install", "chromium"], check=True)
        except:
             pass

def find_free_port(start_port=8000, max_attempts=10):
    """Cherche un port libre à partir du start_port"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port  # Fallback sur 8000 si échec

def main():
    logging.info("Application starting...")
    
    # Vérification et installation automatique de Chromium
    logging.info("Checking for Chromium...")
    if not check_playwright_browsers():
        logging.info("Chromium not found. Installing...")
        install_browsers()
    else:
        logging.info("Chromium is already installed.")
    
    host = "127.0.0.1"
    # Port dynamique pour éviter l'erreur "Address already in use"
    port = find_free_port(8000)
    
    url = f"http://{host}:{port}"
    
    # Lancer le navigateur dans un thread séparé
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    
    # Démarrer le serveur Uvicorn
    # Important: on importe app ici pour éviter des effets de bord avant le setup du logging
    try:
        # On doit ajouter le dossier courant au path pour que les imports de main.py fonctionnent
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # FIX: Import dynamiques pour éviter les erreurs "Could not import module"
        try:
            from main import app
        except ImportError as e:
            logging.critical(f"Failed to import main application: {e}")
            raise e

        # On lance uvicorn programmatiquement en passant l'OBJET app et non la string
        logging.info(f"Starting server on {url}")
        uvicorn.run(app, host=host, port=port, reload=False, workers=1, log_config=None)
        
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
