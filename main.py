from fastapi import *
from auth import *
from models import *
from db import *
from fastapi.security import *
from sqlmodel import *

app = FastAPI()


@app.get("/")
def health():
    return "health"


@app.get("/tasks/")
def get_tasks(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks

@app.post("/tasks/")
def create_task(task: Task, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    if task.id in tasks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"ID {task.id} already exists"
        )

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.get("/tasks/{id}")
def get_task_by_id(id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    q = select(Task).where(id == Task.id)
    res = session.exec(q)
    task = res.first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"item {id} does not exist"
        )
    
    return task


@app.delete("/tasks/{id}")
def delete_task_by_id(id: int, current_user: User = Depends(is_admin), session: Session = Depends(get_session)):
    task = session.get(Task, id)
    if not task: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {id} not found"
        )
    
    session.delete(task)
    session.commit()
    return {"ok", True}

@app.put("/tasks/{id}")
def update_task(id: int, task: TaskUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    task_to_update = session.get(Task, id)

    if not task_to_update: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {id} not found"
        )

    if task.title is not None:
        task_to_update.title = task.title

    if task.description is not None:
        task_to_update.description = task.description

    if task.completed is not None:
        task_to_update.completed = task.completed

    if task.created_at is not None:
        task_to_update.created_at = task.created_at

    session.commit()

    return task_to_update

@app.post("/token")
async def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # Validate username and password
    username = form_data.username
    password = form_data.password

    q = select(User).where(User.username == username)
    res = session.exec(q)
    stored_user = res.first()

    if not stored_user or not verify_password(password, stored_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": username, "role": stored_user.role})
    return {"access_token": token, "token_type": "bearer"}


