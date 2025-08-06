import os
from datetime import datetime

def init_repo():
    os.makedirs(".modelsync", exist_ok=True)
    with open(".modelsync/history.log", "a") as f:
        f.write(f"[{datetime.now()}] Repositório ModelSync iniciado.\n")
    print("Repositório ModelSync inicializado.")

def commit_changes(message: str):
    with open(".modelsync/history.log", "a") as f:
        f.write(f"[{datetime.now()}] Commit: {message}\n")
    print(f"Commit salvo: {message}")