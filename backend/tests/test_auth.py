import pytest
import uuid
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_signup_returns_201():
    response= client.post("/auth/signup", json={
        "email": unique_email(),
        "password": "Password123",
        "full_name" : "Test User"
    })
    assert response.status_code==201

def test_signup_return_token():
    response = client.post("/auth/signup", json={
        "email": unique_email( ),
        "password": "Password123",
        "full_name": "Test User"
    })
    data=response.json()
    assert "access_token" in data

def test_login_with_valid_credentials():
    email= unique_email()
    client.post("/auth/signup", json={
        "email": email,
        "password": "Password123",
        "full_name": "Test User"
    })

    response = client.post("/auth/login", json={
        "email": email,
        "password": "Password123"
    })    
    assert response.status_code ==200

def test_login_with_wrong_password():
    email= unique_email()
    client.post("/auth/signup", json={
        "email": email,
        "password": "Password123",
        "full_name": "Test User"
    })
    response = client.post("/auth/login", json={
        "email": email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_signup_with_duplicate_email():
    email = unique_email()
    client.post("/auth/signup", json={
        "email": email,
        "password": "Password123",
        "full_name": "Test User"

    })

    response = client.post("/auth/signup", json={
        "email": email,
        "password": "Password123",
        "full_name": "Test User"
        
    })
    assert response.status_code != 201