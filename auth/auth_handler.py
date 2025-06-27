import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30)) #type: ignore

def sign_jwt(email: str, role: str, name: str) -> dict:
    if JWT_SECRET is None:
        raise ValueError("JWT_SECRET must be set in the environment variables.")

    payload = {
        "email": email,
        "role": role,
        "name": name,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    }
    return {"access_token": jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)}

def decode_jwt(token: str) -> dict:
    if JWT_SECRET is None:
        raise ValueError("JWT_SECRET must be set in the environment variables.")

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM]) # type: ignore
        return decoded if decoded["exp"] >= datetime.utcnow().timestamp() else {"error": "Token expired"}
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
    except Exception as e:
        return {"error": str(e)}