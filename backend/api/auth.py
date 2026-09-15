from fastapi import APIRouter, HTTPException
from backend.models.schemas import UserRegister, UserLogin 
from backend.core.security import create_access_token
from backend.database.supabase_client import supabase


router =APIRouter(prefix="/auth",tags=["auth"])

@router.post("/signup", status_code =201)
def signup(user: UserRegister):
    """ Register a new user"""
    try: 
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })

        if not response.user:
            raise HTTPException(status_code=400, detail= "Signup Failed")

        token = create_access_token({
            "user_id": response.user.id,
            "email": response.user.email
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": response.user.id,
            "email" :response.user.email
       }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/login")

def login(credentials: UserLogin):
    """ Login with email and password"""

    try:
        response= supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })

        if not response.user:
            raise HTTPException(
                status_code= 401,
                detail= "Invalid email or password"
            )
        token = create_access_token({
            "user_id": response.user.id,
            "email": response.user.email
        })

        return{
            "access_token": token,
            "token_type": "bearer",
            "user_id": response.user.id,
            "email": response.user.email
        }
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))