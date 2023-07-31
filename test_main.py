from fastapi.testclient import TestClient
from main import app
from pydanticmodel import LoginRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

client = TestClient(app)

# Configure test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()


# Test for Home page API
def test_baseurl():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "msg": "Welcome to Softsuave Technologies private limited...."
    }


# Test for successful registration
def test_register_success():
    test_data = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "bmmmmm@gmail.com",
        "password": "secretpassword",
        "mobile_number": "1234567890",
        "age": 30,
    }

    response = client.post("/register/", json=test_data)

    assert response.status_code == 200
    assert response.json() == {
        "message": "Register Completed Successfully",
        "status": "success"
    }


# Test for duplicate email in registration
def test_register_duplicate_email():
    test_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "email": "bmmmnrvv434@gmail.com",  # Already registered email
        "password": "secretpassword2",
        "mobile_number": "9876543210",
        "age": 28,
    }

    response = client.post("/register/", json=test_data)

    assert response.status_code == 400
    assert response.json() == {
        "msg": "email already registered ...",
        "status": "Fail"
    }


# Test for successful login
def test_login_success():
    test_user = {
        "email": "john.doe@example.com",
        "password": "secretpassword"
    }

    response = client.post("/login", json=test_user)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "access_token" in response.json()["tokens"]


# Test for incorrect credentials in login
def test_login_incorrect_credentials():
    test_user = {
        "email": "john.doe@example.com",
        "password": "wrongpassword"
    }

    response = client.post("/login", json=test_user)

    assert response.status_code == 401
    assert response.json()["status"] == "error"
    assert response.json()["msg"] == "entered credentials is incorrect"


# Test for incorrect email in login
def test_login_incorrect_email():
    test_user = {
        "email": "nonexistent@example.com",
        "password": "secretpassword"
    }

    response = client.post("/login", json=test_user)

    assert response.status_code == 401
    assert response.json()["status"] == "error"
    assert response.json()["msg"] == "entered credentials is incorrect"


# Test for changing password with correct credentials
def test_change_password_success():
    test_data = {
        "password": "secretpassword",
        "new_password": "newsecretpassword",
        "confirm_password": "newsecretpassword"
    }

    headers = get_authorization_header("john.doe@example.com", "secretpassword")
    response = client.post("/change_password", json=test_data, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "Success"
    assert response.json()["message"] == "Password Changed Successfully"


# Test for changing password with incorrect credentials
def test_change_password_incorrect_credentials():
    test_data = {
        "password": "wrongpassword",
        "new_password": "newsecretpassword",
        "confirm_password": "newsecretpassword"
    }

    headers = get_authorization_header("john.doe@example.com", "secretpassword")
    response = client.post("/change_password", json=test_data, headers=headers)

    assert response.status_code == 400
    assert response.json() == "Incorrect Password"


# Helper function to get Authorization header for JWT token
def get_authorization_header(email, password):
    test_user = {
        "email": email,
        "password": password
    }

    response = client.post("/login", json=test_user)
    token = response.json()["tokens"]["access_token"]

    return {"Authorization": f"Bearer {token}"}


# Test for refreshing JWT token
def test_refresh_token_success():
    headers = get_authorization_header("john.doe@example.com", "secretpassword")
    response = client.post("/refresh", headers=headers)

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_send_otp_success(test_client, db):
    test_email = "bmmmnrvv434@gmail.com"
    response = test_client.post("/forgotpassword", json={"email_input": test_email})

    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": "Email has been sent successfully."
    }


def test_send_otp_invalid_email(test_client, db):
    test_email = "invalid_email"
    response = test_client.post("/forgotpassword", json={"email_input": test_email})

    assert response.status_code == 400
    assert response.json() == {
        "status_code": 400,
        "message": "Invalid email format."
    }


def test_send_otp_registered_email(test_client, db):
    # Assuming this email is already registered in the database
    test_email = "johndonnn@gmail.com"
    response = test_client.post("/forgotpassword", json={"email_input": test_email})

    assert response.status_code == 400
    assert response.json() == {
        "status_code": 400,
        "message": "Email is already registered."
    }




def test_reset_password_success(test_client, db):
    # Assuming this is a valid OTP present in the test database
    test_data = {
        "otp": "1234",
        "new_password": "resetsecretpassword",
        "confirm_password": "resetsecretpassword"
    }

    response = test_client.post("/forgotchangepassword", json=test_data)

    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Password changed Successfully"


def test_reset_password_invalid_otp(test_client, db):
    test_data = {
        "otp": 1111,
        "new_password": "resetsecretpassword",
        "confirm_password": "resetsecretpassword"
    }

    response = test_client.post("/forgotchangepassword", json=test_data)

    assert response.status_code == 400
    assert response.json()["status_code"] == 400
    assert response.json()["message"] == "Invalid OTP"
