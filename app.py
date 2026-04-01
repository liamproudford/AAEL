
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

@app.route('/health')
def health():
    status = {"swapi": "ok", "db": "ok"}
    http_status = 200

    # Check SWAPI
    try:
        r = requests.get("https://swapi.dev/api/", timeout=5)
        r.raise_for_status()
    except Exception:
        status["swapi"] = "unreachable"
        http_status = 503

    # Check Supabase
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require",
            connect_timeout=5
        )
        conn.close()
    except Exception:
        status["db"] = "unreachable"
        http_status = 503

    return jsonify(status), http_status

#got a new laptop test

if __name__ == '__main__':
    app.run(debug=True)
