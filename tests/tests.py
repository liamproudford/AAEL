import os
from unittest.mock import patch, MagicMock

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _mock_response(json_data=None):
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    mock.json.return_value = json_data or {"results": [], "count": 0}
    return mock


def test_home(client):
    assert client.get('/').status_code == 200


@patch("requests.get")
def test_characters(mock_get, client):
    mock_get.return_value = _mock_response({"results": [], "count": 0})
    assert client.get('/characters').status_code == 200


@patch("requests.get")
def test_health(mock_get, client):
    mock_get.return_value = _mock_response()
    response = client.get('/health')
    assert response.status_code == 200
    assert "status" in response.get_json()


@patch("requests.get")
def test_status(mock_get, client):
    mock_get.return_value = _mock_response()
    response = client.get('/status')
    assert response.status_code == 200
    data = response.get_json()
    assert "database" in data
    assert "swapi" in data
