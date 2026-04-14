import os
import pytest
from unittest.mock import patch, MagicMock

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _mock_get(*args, **kwargs):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    url = args[0] if args else ""
    if "people" in url:
        mock.json.return_value = {
            "results": [{
                "name": "Luke Skywalker",
                "birth_year": "19BBY",
                "height": "172",
                "mass": "77",
                "gender": "male",
                "eye_color": "blue",
                "hair_color": "blond",
                "homeworld": "https://swapi.dev/api/planets/1/",
                "species": [],
                "films": ["f1", "f2"],
            }],
            "count": 82,
        }
    elif "planets" in url:
        mock.json.return_value = {"name": "Tatooine"}
    else:
        mock.json.return_value = {}
    return mock


# ── Basic routes ────────────────────────────────────────────

def test_home(client):
    assert client.get('/').status_code == 200


def test_characters_returns_page(client):
    with patch("requests.get", side_effect=_mock_get):
        assert client.get('/characters').status_code == 200


def test_graceful_degradation_on_upstream_failure(client):
    import requests as req
    with patch("requests.get", side_effect=req.RequestException("SWAPI down")):
        assert client.get('/characters').status_code == 503


# ── Health / status ─────────────────────────────────────────

def test_health_endpoint_reports_ok_when_both_up(client):
    with patch("requests.get", side_effect=_mock_get):
        response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_health_endpoint_degraded_when_services_down(client):
    import requests as req
    with patch("requests.get", side_effect=req.RequestException("down")):
        response = client.get('/health')
    assert response.status_code == 503
    assert response.get_json()["status"] == "degraded"


def test_status_returns_dependency_breakdown(client):
    with patch("requests.get", side_effect=_mock_get):
        response = client.get('/status')
    assert response.status_code == 200
    data = response.get_json()
    assert "database" in data
    assert "swapi" in data


# ── Quiz ────────────────────────────────────────────────────

def test_quiz_loads(client):
    with patch("requests.get", side_effect=_mock_get):
        assert client.get('/quiz').status_code == 200


def test_quiz_correct_guess_gives_score(client):
    with patch("requests.get", side_effect=_mock_get):
        client.get('/quiz')
    with client.session_transaction() as sess:
        sess['character_name'] = 'Luke Skywalker'
        sess['clues'] = [["Homeworld", "Tatooine"]]
        sess['clues_shown'] = 1
        sess['state'] = 'playing'
    response = client.post('/quiz', data={"guess": "Luke Skywalker"})
    assert response.status_code == 200
    assert b'correct' in response.data.lower() or b'score' in response.data.lower()


def test_quiz_submit_blocked_without_correct_state(client):
    response = client.post('/quiz/submit', data={"username": "testuser"})
    assert response.status_code == 302  # redirects to /quiz
