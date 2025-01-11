import bcrypt

def hash_password(password: str) -> str:
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes, salt)
    return hashed.decode("utf-8")

tasks = {
    1: {"id": 1, "title": "Task 1", "description": "First task", "completed": False},
    2: {"id": 2, "title": "Task 2", "description": "Second task", "completed": False},
}

users = {
    1: {"username": "linkimos", "password": hash_password("password123"), "role": "admin"},
    2: {"username": "may", "password": hash_password("userpassword"), "role": "user"},
}
