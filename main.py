from fastapi import FastAPI, HTTPException, status, Depends
from auth import *
from db import tasks, users
from models import Task
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI()


@app.get("/")
def health():
    return "health"


@app.get("/tasks/")
def get_tasks(current_user: dict = Depends(get_current_user)):
    return tasks


@app.post("/tasks/")
def create_task(task: Task, current_user: dict = Depends(get_current_user)):
    if task.id in tasks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"ID {task.id} already exists"
        )

    tasks[task.id] = task
    return task


@app.get("/tasks/{id}")
def get_task_by_id(id: int, current_user: dict = Depends(get_current_user)):
    if id in tasks:
        return tasks[id]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"item {id} does not exist"
    )


@app.delete("/tasks/{id}")
def delete_task_by_id(id: int, current_user: dict = Depends(is_admin)):
    if id in tasks:
        deleted_task = tasks.pop(id)
        return deleted_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {id} not found"
    )


@app.post("/token")
async def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate username and password
    username = form_data.username
    password = form_data.password
    for stored_user in users.values():
        if stored_user["username"] == username:
            if verify_password(password, stored_user["password"]):
                token = create_access_token(data={"sub": username, "role": stored_user["role"]})
                return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )