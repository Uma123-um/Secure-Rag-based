from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from pwdlib import PasswordHash


# ============================================================
# JWT CONFIGURATION
# ============================================================

SECRET_KEY = "change-this-secret-key-in-production"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


# ============================================================
# DEMO USERS
# ============================================================

users_db = {

    "uma": {
        "username": "uma",
        "password": password_hash.hash("uma123"),
        "department": "HR"
    },

    "rahul": {
        "username": "rahul",
        "password": password_hash.hash("rahul123"),
        "department": "Finance"
    },

    "amit": {
        "username": "amit",
        "password": password_hash.hash("amit123"),
        "department": "Legal"
    },

 "priya": {
        "username": "priya",
        "password": password_hash.hash("priya123"),
        "department": "salary"
    }

}


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(plain_password, hashed_password):

    return password_hash.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# USER AUTHENTICATION
# ============================================================

def authenticate_user(username, password):

    user = users_db.get(username)
    print("authenticating user:", username, "user found:", user, "password match:", verify_password(password, user["password"]) if user else None)

    if not user:
        return None

    if not verify_password(password, user["password"]):
        return None

    return user


# ============================================================
# CREATE JWT TOKEN
# ============================================================

def create_access_token(user):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {

        "sub": user["username"],

        "username": user["username"],

        "department": user["department"],

        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# ============================================================
# VERIFY JWT TOKEN
# ============================================================

def verify_token(token):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("username")

        department = payload.get("department")

        if not username or not department:
            return None

        return {
            "username": username,
            "department": department
        }

    except JWTError:

        return None