import pytest
from backend.core.security import(
    hash_password,
    verify_password,
    create_access_token,
    verify_token,    
)

def test_hash_password_returns_different_value():
    password="MyPassword123"
    hashed=hash_password(password)
    assert hashed != password



def test_hash_is_different_each_time():
    """Same password → different hash every time (bcrypt salting)"""
    hash1 = hash_password("mypassword123")
    hash2 = hash_password("mypassword123")
    assert hash1 != hash2   

