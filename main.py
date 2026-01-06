
from fastapi import FastAPI, BackgroundTasks
from bot_engine import LBCPoster
import uvicorn

app = FastAPI(title="LBC Automation API")

@app.get("/")
def home():
    return {"status": "online", "message": "LBC Automation API is running"}

@app.post("/start-posting")
def start_posting(background_tasks: BackgroundTasks):
    """
    Lance le processus de publication en arrière-plan.
    Retourne immédiatemment pour ne pas bloquer le client.
    """
    poster = LBCPoster()
    
    # On délègue l'exécution à une tâche de fond (BackgroundTasks)
    # pour que l'API réponde tout de suite "OK"
    background_tasks.add_task(poster.start_process) 
    
    return {
        "status": "started", 
        "details": "L'automatisation a démarré en tâche de fond. Regardez le terminal pour les logs."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
