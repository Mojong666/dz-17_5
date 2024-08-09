from fastapi import FastAPI
from backend import task, user
from backend.db import init_db

app = FastAPI()

app.include_router(task.router)
app.include_router(user.router)

@app.get('/')
def root():
    return {"message": "Welcome to Taskmanager"}

init_db()
