
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from bot_engine import LBCPoster
import uvicorn
import asyncio
import json

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
                
                # Create bot instance
                poster = LBCPoster()
                manager.bot_instance = poster
                
                # Run bot in executor (thread pool) to not block WebSocket
                loop = asyncio.get_event_loop()
                
                # This will run the bot synchronously in a thread
                # For now, we'll use the simple version without streaming callback
                # In production, we'd need to refactor bot_engine to be async-friendly
                loop.run_in_executor(None, poster.start_process)
                
                await websocket.send_json({
                    "type": "status",
                    "message": "Bot démarré ! (Mode test - pas de streaming pour l'instant)"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WebSocket] Client disconnected")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
