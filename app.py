
from flask import Flask, jsonify, render_template, request
import requests
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/characters')
def get_characters():
    page = request.args.get('page', 1, type=int)
    response = requests.get(f"https://swapi.dev/api/people/?page={page}")
    data = response.json()
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
    conn = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )
    conn.close()
    return jsonify({"status": "Database connected!"})


# Leaderboard page
@app.route('/leaderboard')
def leaderboard():
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require"
        )

        cur = conn.cursor()
        cur.execute('SELECT name, score FROM "Leaderboard" ORDER BY score DESC LIMIT 10;')
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('leaderboard.html', scores=rows)

    except psycopg.Error as e:
        return jsonify({
            "error": "Unable to load leaderboard",
            "details": str(e)
        }), 503

def _check_db():
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require"
        )
        conn.close()
        return True, None
    except psycopg.Error as e:
        return False, str(e)


def _check_swapi():
    try:
        response = requests.get("https://swapi.dev/api/people/1/", timeout=5)
        response.raise_for_status()
        return True, None
    except requests.RequestException as e:
        return False, str(e)


@app.route('/health')
def health():
    db_ok, _ = _check_db()
    swapi_ok, _ = _check_swapi()
    if db_ok and swapi_ok:
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "degraded"}), 503


@app.route('/status')
def status():
    db_ok, db_err = _check_db()
    swapi_ok, swapi_err = _check_swapi()
    return jsonify({
        "database": {"ok": db_ok, "error": db_err},
        "swapi": {"ok": swapi_ok, "error": swapi_err},
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
