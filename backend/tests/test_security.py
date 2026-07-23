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


def test_verify_correct_password():
    """Correct password must return True"""
    hashed = hash_password("mypassword123")
    assert verify_password("mypassword123", hashed) == True


def test_create_and_verify_token():
    """Token we create must be verifiable"""
    token = create_access_token({"user_id": "123", "email": "test@test.com"})
    payload = verify_token(token)
    assert payload["user_id"] == "123"
    assert payload["email"] == "test@test.com"


