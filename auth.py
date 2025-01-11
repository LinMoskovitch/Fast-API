import jwt
import bcrypt
from datetime import timedelta, datetime, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from db import users

# mock
SECRET_KEY = "6ed033ff2edc3d16009c10e98848bb1e947c57b66b7868ec3f84f15691481fe1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(bytes, hashed_bytes)


def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        decoded_jwt = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded_token = decode_access_token(token)
    username = decoded_token.get("sub")  # Extract the "sub" claim

    for user in users.values():
        if user["username"] == username:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def is_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to perform this action")
    return True
