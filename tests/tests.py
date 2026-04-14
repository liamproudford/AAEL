import os
from unittest.mock import patch, MagicMock

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"

from app import app


def _mock_response(json_data=None):
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    mock.json.return_value = json_data or {"results": [], "count": 0}
    return mock


def test_home():
    client = app.test_client()
    assert client.get('/').status_code == 200


@patch("app.requests.get")
def test_characters(mock_get):
    client = app.test_client()
    mock_get.return_value = _mock_response({"results": [], "count": 0})
    assert client.get('/characters').status_code == 200


@patch("app.requests.get")
def test_health(mock_get):
    client = app.test_client()
    mock_get.return_value = _mock_response()
    response = client.get('/health')
    assert response.status_code == 200
    assert "status" in response.get_json()


@patch("app.requests.get")
def test_status(mock_get):
    client = app.test_client()
    mock_get.return_value = _mock_response()
    response = client.get('/status')
    assert response.status_code == 200
    data = response.get_json()
    assert "database" in data
    assert "swapi" in data