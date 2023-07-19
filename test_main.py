from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_baseurl():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code":200,
        "msg":"Welcome to Softsuave Technologies private limited...."
    }