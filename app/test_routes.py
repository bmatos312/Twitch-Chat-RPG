import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b"About" in response.data
