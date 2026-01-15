
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from bot_engine import LBCPoster, get_session_filename
from utils import BASE_PATH
import uvicorn
import asyncio
import os
import glob
from pathlib import Path
import importlib
import sys

app = FastAPI(title="LBC Automation API")

# Serve static files (HTML, JS, CSS) - Compatible exe
static_dir = BASE_PATH / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.bot_instance = None
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Modèle de configuration
class AccountCredentials(BaseModel):
    email: str
    password: str

class ConfigData(BaseModel):
    accounts: List[AccountCredentials]  # Liste de comptes au lieu d'un seul
    sheet_name: str
    img_folder: str  # REQUIS - Le client doit le configurer
    max_ads: int = 3
    delay_min: int = 60
    delay_max: int = 120
    real_posting: bool = True
    browser_mode: str = "minimized"
    captcha_wait: int = 300

# Endpoints de configuration
@app.get("/api/config")
async def get_config():
    """Récupère la configuration multi-comptes actuelle (sans les mots de passe)"""
    config_file = BASE_PATH / "config.env"
    
    if not config_file.exists():
        # Retourner les valeurs par défaut avec un compte vide
        return {
            "accounts": [{"email": ""}],
            "sheet_name": "LBC-Automation",
            "img_folder": "",
            "max_ads": 3,
            "delay_min": 60,
            "delay_max": 120,
            "real_posting": True,
            "browser_mode": "minimized",
            "captcha_wait": 300
        }
    
    # Lire le fichier config.env
    config = {}
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                config[key] = value
    
    # Charger tous les comptes
    num_accounts = int(config.get("NUM_ACCOUNTS", "1"))
    accounts = []
    for i in range(1, num_accounts + 1):
        email = config.get(f"ACCOUNT_{i}_EMAIL", "")
        if email:
            accounts.append({"email": email})  # Ne pas retourner les mots de passe
    
    # Si aucun compte multi, essayer l'ancien format
    if not accounts:
        email = config.get("LEBONCOIN_EMAIL", "")
        if email:
            accounts.append({"email": email})
    
    # Retourner la config
    return {
        "accounts": accounts if accounts else [{"email": ""}],
        "sheet_name": config.get("GOOGLE_SHEET_NAME", "LBC-Automation"),
        "img_folder": config.get("IMG_FOLDER", ""),
        "max_ads": int(config.get("MAX_ADS_PER_RUN", "3")),
        "delay_min": int(config.get("DELAY_BETWEEN_ADS_MIN", "60")),
        "delay_max": int(config.get("DELAY_BETWEEN_ADS_MAX", "120")),
        "real_posting": config.get("ENABLE_REAL_POSTING", "true").lower() == "true",
        "browser_mode": config.get("BROWSER_MODE", "minimized"),
        "captcha_wait": int(config.get("CAPTCHA_MAX_WAIT", "300"))
    }

@app.post("/api/config")
async def save_config(config: ConfigData):
    """Sauvegarde la configuration multi-comptes dans config.env"""
    config_file = BASE_PATH / "config.env"
    
    # Charger la config existante pour préserver les paramètres avancés
    existing_config = {}
    if config_file.exists():
        with open(str(config_file), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_config[key.strip()] = value.strip()
    
    # Construire la section des comptes
    num_accounts = len(config.accounts)
    accounts_section = ""
    for i, account in enumerate(config.accounts, start=1):
        accounts_section += f"\n# --- Compte {i} ---\n"
        accounts_section += f"ACCOUNT_{i}_EMAIL={account.email}\n"
        accounts_section += f"ACCOUNT_{i}_PASSWORD={account.password}\n"
    
    # Nettoyer les anciens fichiers de session pour les comptes supprimés
    print(f"[Config] Nettoyage des sessions obsolètes (comptes actuels: {num_accounts})")
    
    # Créer un ensemble des fichiers de session valides (basés sur les emails configurés)
    valid_session_files = {get_session_filename(account.email) for account in config.accounts}
    
    # Trouver tous les fichiers de session existants
    existing_session_files = glob.glob("state_account_*.json")
    cleaned_count = 0
    
    for session_file in existing_session_files:
        # Si ce fichier ne correspond à aucun email configuré, le supprimer
        if session_file not in valid_session_files:
            try:
                print(f"[Config] Suppression session obsolète : {session_file}")
                os.remove(session_file)
                cleaned_count += 1
            except OSError as e:
                print(f"[Config] Erreur suppression {session_file}: {e}")
    
    if cleaned_count > 0:
        print(f"[Config] ✅ {cleaned_count} fichier(s) de session supprimé(s)")
    else:
        print(f"[Config] ✅ Aucun fichier de session à nettoyer")
    
    # Créer le contenu du fichier
    content = f"""# ==================== CONFIGURATION LBC AUTOMATION ====================
# Fichier généré automatiquement via l'interface web
# Multi-Comptes : {num_accounts} compte(s) configuré(s)
# Dernière modification : {asyncio.get_event_loop().time()}
# ⚠️ NE PARTAGEZ JAMAIS CE FICHIER !
# ======================================================================

# ==================== COMPTES LEBONCOIN ====================
NUM_ACCOUNTS={num_accounts}
{accounts_section}

# ==================== GOOGLE SHEETS ====================
GOOGLE_SHEET_NAME={config.sheet_name}

# ==================== DOSSIER PHOTOS ====================
IMG_FOLDER={config.img_folder}

# ==================== PUBLICATION ====================
MAX_ADS_PER_RUN={config.max_ads}
DELAY_BETWEEN_ADS_MIN={existing_config.get('DELAY_BETWEEN_ADS_MIN', '60')}
DELAY_BETWEEN_ADS_MAX={existing_config.get('DELAY_BETWEEN_ADS_MAX', '120')}
ENABLE_REAL_POSTING={existing_config.get('ENABLE_REAL_POSTING', 'true')}

# ==================== MODE NAVIGATEUR ====================
BROWSER_MODE={existing_config.get('BROWSER_MODE', 'minimized')}

# ==================== CAPTCHA ====================
CAPTCHA_MAX_WAIT={existing_config.get('CAPTCHA_MAX_WAIT', '300')}
CAPTCHA_MODE={existing_config.get('CAPTCHA_MODE', 'manual')}
"""
    
    # Écrire le fichier
    with open(str(config_file), 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Configuration multi-comptes sauvegardée : {num_accounts} compte(s)")
    
    # Recharger le module config pour appliquer les changements immédiatement
    try:
        import config
        import bot_engine
        
        # Recharger les modules pour prendre en compte la nouvelle config
        importlib.reload(config)
        importlib.reload(bot_engine)
        
        print(f"✅ Configuration rechargée automatiquement")
    except Exception as e:
        print(f"⚠️ Avertissement : Impossible de recharger la config automatiquement ({e})")
        print(f"   Veuillez relancer le serveur pour appliquer les changements")
    
    return {
        "status": "success", 
        "message": f"✅ Configuration sauvegardée et rechargée : {num_accounts} compte(s) configuré(s)"
    }

@app.get("/config-page", response_class=HTMLResponse)
async def config_page():
    """Sert la page de configuration"""
    try:
        config_html_path = BASE_PATH / "static" / "config.html"
        with open(str(config_html_path), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Page de configuration introuvable")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main HTML interface"""
    try:
        index_html_path = BASE_PATH / "static" / "index.html"
        with open(str(index_html_path), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Interface en cours de création...</h1>")

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming browser screenshots
    and receiving user input (clicks, keyboard)
    """
    await manager.connect(websocket)
    print("[WebSocket] Client connected")
    
    try:
        while True:
            # Receive messages from frontend
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "start":
                # Start the bot with streaming
                print("[WebSocket] Starting bot with streaming...")
                
                # Send initial status
                await websocket.send_json({
                    "type": "status",
                    "message": "Initialisation du bot..."
                })
                
                # Create callback for thread-safe WebSocket messages
                loop = asyncio.get_event_loop()
                
                def ws_callback(message):
                    """Thread-safe callback pour envoyer des messages WebSocket depuis le bot"""
                    asyncio.run_coroutine_threadsafe(
                        manager.broadcast(message),
                        loop
                    )
                
                # Create bot instance with WebSocket callback
                poster = LBCPoster(ws_callback=ws_callback)
                manager.bot_instance = poster
                
                # Run bot in executor (thread pool) to not block WebSocket
                
                # Fonction wrapper pour nettoyer après l'exécution
                async def run_and_notify():
                    result = "ERROR_UNKNOWN"
                    try:
                        # Utiliser la méthode multi-comptes (gère aussi le cas d'un seul compte)
                        result = await loop.run_in_executor(None, poster.start_multi_account_process)
                        print(f"[Bot] Terminé avec résultat : {result}")
                    except Exception as e:
                        print(f"[Bot] Erreur lors de l'exécution : {type(e).__name__}: {e}")
                        result = f"ERROR_{type(e).__name__}"
                    finally:
                        # Nettoyage
                        manager.bot_instance = None
                        
                        # Notifier le frontend
                        await manager.broadcast({
                            "type": "bot_stopped",
                            "result": result
                        })
                
                # Lancer le bot de manière asynchrone
                asyncio.create_task(run_and_notify())
                
                await websocket.send_json({
                    "type": "status",
                    "message": "Bot démarré - Connexion au Google Sheet..."
                })
            
            elif data.get("type") == "stop":
                # Stop the bot
                print("[WebSocket] Stop command received")
                
                if manager.bot_instance:
                    # Set stop flag (bot will check this and close browser itself)
                    manager.bot_instance.should_stop = True
                    print("[WebSocket] Stop flag set - bot will terminate gracefully")
                    
                    await websocket.send_json({
                        "type": "status",
                        "message": "Arrêt demandé - le bot va se terminer..."
                    })
                else:
                    await websocket.send_json({
                        "type": "status",
                        "message": "Aucun bot en cours d'exécution"
                    })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WebSocket] Client disconnected")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
