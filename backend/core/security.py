# authentication and security handling
from passlib.context import CryptContext
import jwt 
from datetime import datetime, timedelta



pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str)-> str:
    return pwd_context.hash(password)


verify_password():



create_access_token():



verify_token():


get_current_user():