from datetime import datetime, timedelta
from json import load
from dotenv import load_dotenv
import os
from jose import jwt

from app.libs.formart.response import CustomException

load_dotenv()
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    from jose import JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id", [])
        role: list = payload.get("role", [])
        if id is None or role is None:
            raise ValueError("Invalid token")
        return {"user": id, "role": role}
    except JWTError:
        raise CustomException(500, "Sever Error")
