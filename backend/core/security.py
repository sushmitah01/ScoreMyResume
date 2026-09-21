# authentication and security handling
from passlib.context import CryptContext
import jwt 
from datetime import datetime, timedelta, timezone
from backend.core.config import SUPABASE_JWT_SECRET
from fastapi import Header, HTTPException

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str)-> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed:str)-> str:
    return pwd_context.verify(plain,hashed)

SECRET_KEY= SUPABASE_JWT_SECRET or "dev-secret-key"
ALGORITHM = "HS256"
EXPIRE_MIN= 60*24

def create_access_token(data: dict)->str:
    payload= data.copy()
    expire = datetime.now(timezone.utc) +timedelta(minutes=EXPIRE_MIN)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str)-> dict:
    try:
        return jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def get_current_user(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload   
    

