from app import app

client = app.test_client()
def test_home():
    assert client.get('/').status_code == 200

def test_characters():
    assert client.get('/characters').status_code == 200

def test_db():
    assert client.get('/db').status_code == 200

def test_characters_has_results():
    response = client.get('/characters')
    assert 'results' in response.get_json()



