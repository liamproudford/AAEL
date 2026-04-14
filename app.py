
from flask import Flask, jsonify, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def _supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }


def _check_swapi():
    try:
        response = requests.get("https://swapi.dev/api/people/1/", timeout=5)
        response.raise_for_status()
        return True, None
    except requests.RequestException as e:
        return False, str(e)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/characters')
def get_characters():
    page = request.args.get('page', 1, type=int)
    try:
        response = requests.get(f"https://swapi.dev/api/people/?page={page}", timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return render_template('error.html', message="Could not fetch characters from SWAPI"), 503
    characters = data.get('results', [])
    total = data.get('count', 0)
    total_pages = -(-total // 10)  # ceiling division
    return render_template(
        'characters.html',
        characters=characters,
        page=page,
        total_pages=total_pages
    )


@app.route('/test-db')
def test_db():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=_supabase_headers(),
            timeout=5
        )
        response.raise_for_status()
        return jsonify({"status": "Database connected!"}), 200
    except requests.RequestException as e:
        return jsonify({"status": "Database connection failed", "error": str(e)}), 503


# Leaderboard page
@app.route('/leaderboard')
def leaderboard():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/Leaderboard?select=*&order=score.desc&limit=10",
            headers=_supabase_headers(),
            timeout=5
        )
        response.raise_for_status()
        scores = response.json()
        return render_template('leaderboard.html', scores=scores)
    except requests.RequestException as e:
        return jsonify({"error": "Unable to load leaderboard"}), 503


@app.route('/health')
def health():
    try:
        db_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=_supabase_headers(),
            timeout=5
        )
        db_response.raise_for_status()
        db_ok = True
    except requests.RequestException:
        db_ok = False
    swapi_ok, _ = _check_swapi()
    if db_ok and swapi_ok:
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "degraded"}), 503


@app.route('/status')
def status():
    db_err = None
    try:
        db_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=_supabase_headers(),
            timeout=5
        )
        db_response.raise_for_status()
        db_ok = True
    except requests.RequestException as e:
        db_ok = False
        db_err = str(e)
    swapi_ok, swapi_err = _check_swapi()
    return jsonify({
        "database": {"ok": db_ok, "error": db_err},
        "swapi": {"ok": swapi_ok, "error": swapi_err},
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
