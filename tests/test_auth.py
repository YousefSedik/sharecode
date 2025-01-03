from fastapi.testclient import TestClient
from main import app

# Create a TestClient instance
client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}


def test_read_item():
    item_id = 42
    response = client.get(f"/items/{item_id}?q=test_query")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "q": "test_query"}
