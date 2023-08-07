from fastapi.testclient import TestClient
from main import app
from pydanticmodel import LoginRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from fastapi_jwt_auth import AuthJWT

client = TestClient(app)
acc_token=""
sample_user = {
    "firstname": "John",
    "lastname": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword",
    "mobile_number": "1234567890",
    "age": 30,
}

# Configure test database
TEST_DATABASE_URL = 'postgresql://postgres:postgres@172.25.0.2/chatbook'
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
        "email": "bmmmyyyyyyyyyyymmmmm@gmail.com",
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
def test_register_unprocessable():
    test_data = {
        "firstname": "John",
        "lastname": "Doe"
    }

    response = client.post("/register/", json=test_data)

    assert response.status_code == 422
    assert response.json() == {"message":"Required fields are missing","status":"Fail"}


# Test for check email type is valid or not 
def test_check_Invalid_email_type():
    test_data = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "bmmmyyyyyyyyyyymmm",
        "password": "secretpassword",
        "mobile_number": "1234567890",
        "age": 30,
    }
    response = client.post("/register/",json=test_data)
    assert response.status_code == 400
    assert response.json() == {
        "message": "Invalid email Type",
        "status":"Fail"
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
        "email": "bmmm@gmail.com",
        "password": "stringst"
    }

    response = client.post("/login", json=test_user)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "access_token" in response.json()["tokens"]
    if "access_token" in response.json()["tokens"]:
        acc_token=response.json()["tokens"]
        

# login unprocessable operation
def test_login_unprocessable():
    test_user = {
        "email": "john.doe@example.com",
    }
    response = client.post("/login", json=test_user)
    assert response.status_code == 422
    assert response.json()=={"message":"Required fields are missing","status":"Fail"}

# Test for incorrect credentials in login
def test_login_incorrect_credentials():
    test_user = {
        "email": "john.doe@example.com",
        "password": "wrongpassword234"
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
        "password": "stringst",
        "new_password": "stringst",
        "confirm_password": "stringst"
    }

    headers = get_authorization_header("bmmm@gmail.com", "stringst")
    response = client.put("/change_password", json=test_data, headers=headers)

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

    headers = get_authorization_header("bmmm@gmail.com", "stringst")
    response = client.put("/change_password", json=test_data, headers=headers)

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




def test_refresh_token_success():
    # Assuming you have the necessary imports and fixtures set up

    # Create a test user
    test_user = {
        "email": "bmmm@gmail.com",
        "password": "stringst"
    }

    # Register the test user and obtain the refresh token
    client.post("/register", json=test_user)
    response = client.post("/login", json=test_user)
    refresh_token = response.json()["tokens"]["refresh_token"]

    # Use the refresh token in the Authorization header
    headers = {"Authorization": f"Bearer {refresh_token}"}

    # Send the request to the /refresh endpoint
    response = client.post("/refresh", headers=headers)

    # Assert the response
    assert response.status_code == 200
    assert "access_token" in response.json()



def test_send_otp_success(test_client, db):
    test_email = "bmmmnrvv434@gmail.com"
    response = client.put(f"/forgotpassword/{test_email}")

    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": "Email has been sent successfully."
    }


def test_send_otp_invalid_email(test_client, db):
    test_email = "bmmmnrvv43444@gmail.com"
    response = client.put(f"/forgotpassword/{test_email}")

    assert response.status_code == 400
    assert response.json() == {
            "statusCode":400,
            "message":"Entered User id is Invalid..",
            "status":"Fail"
        }




def test_reset_password_success(test_client, db):
    # Assuming this is a valid OTP present in the test database
    test_data = {
        "otp": 3037,
        "new_password": "stringst",
        "confirm_password": "stringst"
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
