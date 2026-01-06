
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from pydantic import BaseModel
from bot_engine import LBCPoster
import uvicorn
import asyncio
import json
import os
from pathlib import Path

app = FastAPI(title="LBC Automation API")

# Serve static files (HTML, JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
class ConfigData(BaseModel):
    email: str
    password: str
    sheet_name: str
    max_ads: int = 3
    delay_min: int = 300
    delay_max: int = 600
    real_posting: bool = False
    browser_mode: str = "minimized"
    captcha_wait: int = 300

# Endpoints de configuration
@app.get("/api/config")
async def get_config():
    """Récupère la configuration actuelle (sans le mot de passe pour sécurité)"""
    config_file = Path("config.env")
    
    if not config_file.exists():
        # Retourner les valeurs par défaut
        return {
            "email": "",
            "sheet_name": "LBC-Automation",
            "max_ads": 3,
            "delay_min": 300,
            "delay_max": 600,
            "real_posting": False,
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
    
    # Retourner la config (sans le mot de passe)
    return {
        "email": config.get("LEBONCOIN_EMAIL", ""),
        "sheet_name": config.get("GOOGLE_SHEET_NAME", "LBC-Automation"),
        "max_ads": int(config.get("MAX_ADS_PER_RUN", "3")),
        "delay_min": int(config.get("DELAY_BETWEEN_ADS_MIN", "300")),
        "delay_max": int(config.get("DELAY_BETWEEN_ADS_MAX", "600")),
        "real_posting": config.get("ENABLE_REAL_POSTING", "false").lower() == "true",
        "browser_mode": config.get("BROWSER_MODE", "minimized"),
        "captcha_wait": int(config.get("CAPTCHA_MAX_WAIT", "300"))
    }

@app.post("/api/config")
async def save_config(config: ConfigData):
    """Sauvegarde la configuration dans config.env"""
    config_file = Path("config.env")
    
    # Créer le contenu du fichier
    content = f"""# ==================== CONFIGURATION LBC AUTOMATION ====================
# Fichier généré automatiquement via l'interface web
# Dernière modification : {asyncio.get_event_loop().time()}
# ⚠️ NE PARTAGEZ JAMAIS CE FICHIER !
# ======================================================================

# ==================== IDENTIFIANTS LEBONCOIN ====================
LEBONCOIN_EMAIL={config.email}
LEBONCOIN_PASSWORD={config.password}

# ==================== GOOGLE SHEETS ====================
GOOGLE_SHEET_NAME={config.sheet_name}

# ==================== PUBLICATION ====================
MAX_ADS_PER_RUN={config.max_ads}
DELAY_BETWEEN_ADS_MIN={config.delay_min}
DELAY_BETWEEN_ADS_MAX={config.delay_max}
ENABLE_REAL_POSTING={'true' if config.real_posting else 'false'}

# ==================== MODE NAVIGATEUR ====================
BROWSER_MODE={config.browser_mode}

# ==================== CAPTCHA ====================
CAPTCHA_MAX_WAIT={config.captcha_wait}
CAPTCHA_MODE=manual
"""
    
    # Écrire le fichier
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Configuration sauvegardée dans {config_file}")
    
    return {"status": "success", "message": "Configuration sauvegardée avec succès"}

@app.get("/config-page", response_class=HTMLResponse)
async def config_page():
    """Sert la page de configuration"""
    try:
        with open("static/config.html", "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Page de configuration introuvable")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main HTML interface"""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Interface en cours de création...</h1>")

@app.post("/start-posting")
def start_posting(background_tasks: BackgroundTasks):
    """
    Lance le processus de publication en arrière-plan.
    Retourne immédiatement pour ne pas bloquer le client.
    """
    # Guard: prevent multiple instances
    if manager.bot_instance is not None:
        return {
            "status": "already_running",
            "details": "Le bot est déjà en cours d'exécution."
        }
    
    poster = LBCPoster()
    manager.bot_instance = poster
    
    # On délègue l'exécution à une tâche de fond (BackgroundTasks)
    # pour que l'API réponde tout de suite "OK"
    def run_and_cleanup():
        poster.start_process()
        manager.bot_instance = None  # Reset after completion
    
    background_tasks.add_task(run_and_cleanup) 
    
    return {
        "status": "started", 
        "details": "L'automatisation a démarré en tâche de fond. Regardez le terminal pour les logs."
    }

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
            # Receive messages from frontend (clicks, keyboard events)
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "click":
                # Forward click to bot instance
                if manager.bot_instance:
                    x, y = data.get("x"), data.get("y")
                    # TODO: Inject click into Playwright
                    print(f"[WebSocket] Click received at ({x}, {y})")
            
            elif data.get("type") == "start":
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
                    result = await loop.run_in_executor(None, poster.start_process)
                    print(f"[Bot] Terminé avec résultat : {result}")
                    
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
                    "message": "Bot démarré ! (Mode test - pas de streaming pour l'instant)"
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
