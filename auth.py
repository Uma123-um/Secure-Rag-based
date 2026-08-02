import os
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"


def create_token(username: str, department: str):
    payload = {
        "username": username,
        "department": department
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None