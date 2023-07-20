from fastapi.testclient import TestClient
from main import app
from schema import Book
from schema import Book as SchemaBook
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Book as ModelBook
from pydanticmodel import ChangePasswordRequest, LoginRequest,Forgotchangepassword
from fastapi_jwt_auth import AuthJWT
from schema import Book as SchemaBook
from models import Book as ModelBook
import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from pydanticmodel import LoginRequest
from fastapi_jwt_auth.exceptions import AuthJWTException


load_dotenv('.env')

engine = create_engine(os.environ['DATABASE_URL'])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


client = TestClient(app)
def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




# for Home page api
def test_baseurl():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code":200,
        "msg":"Welcome to Softsuave Technologies private limited...."
    }

# for register api

def test_register_success():
    # Test data for successful registration
    test_data = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "bmmm@gmail..com",
        "password": "secretpassword",
        "mobile_number": "1234567890",
        "age": "30",
        "token": "sometoken"
    }

    # Send POST request to the API
    response = client.post("/register/", json=test_data)

    # Print the response content to see the error message
    print(response.json())

    # Assert the response status code and content
    assert response.status_code == 200
    assert response.json() == {
        "message": "Register Completed Successfully",
        "status": "success"
    }

def test_register_duplicate_email():
    # Test data with duplicate email
    test_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "email": "john.doe@example.com",  # Already registered email
        "password": "secretpassword2",
        "mobile_number": "9876543210",
        "age": 28,
        "token": "anothertoken"
    }

    # Send POST request to the API
    response = client.post("/register/", json=test_data)

    # Assert the response status code and content
    assert response.status_code == 400
    assert response.json() == {
        "msg": "email is already registered..",
        "status_code": 400
    }

# for login api

def test_login_success():
    # Test data for successful login
    test_user = {
        "email": "john.doe@gmail.com",
        "password": "secretpassword"
    }

    # Send POST request to the API
    response = client.post("/login", json=test_user)

    # Assert the response status code and content
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "access_token" in response.json()["tokens"]

def test_login_incorrect_credentials():
    # Test data with incorrect credentials
    test_user = {
        "email": "john.doe@gmail.com",
        "password": "wrongpassword"
    }

    # Send POST request to the API
    response = client.post("/login", json=test_user)

    # Assert the response status code and content
    assert response.status_code == 401
    assert response.json()["status"] == "error"
    assert response.json()["msg"] == "entered credentials is incorrect"

def test_login_incorrect_email():
    # Test data with incorrect email address
    test_user = {
        "email": "nonexistent@example.com",
        "password": "secretpassword"
    }

    # Send POST request to the API
    response = client.post("/login", json=test_user)

    # Assert the response status code and content
    assert response.status_code == 401
    assert response.json()["status"] == "error"
    assert response.json()["msg"] == "entered credentials is incorrect"