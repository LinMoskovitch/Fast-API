import bcrypt
from sqlmodel import SQLModel, create_engine, Session, select
from models import *

def hash_password(password: str) -> str:
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes, salt)
    return hashed.decode("utf-8")

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def seed_data():
    with Session(engine) as session:
        # Add tasks if the table is empty
        if not session.exec(select(Task)).first():
            task1 = Task(title="Buy groceries", description="Milk, Bread, Eggs", completed=False)
            task2 = Task(title="Complete project", description="Finish FastAPI app", completed=True)
            session.add(task1)
            session.add(task2)
        
        # Add users if the table is empty
        if not session.exec(select(User)).first():
            user1 = User(username="admin", password=hash_password("pass123"), role="admin")
            user2 = User(username="user", password=hash_password("pass456"), role="user")
            session.add(user1)
            session.add(user2)
        
        # Commit changes
        session.commit()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized!")
