
from flask import Flask, jsonify, render_template, request
from datetime import datetime, timezone
import time
import requests
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Track when app started
START_TIME = time.time()
APP_VERSION = "1.0"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/characters')
def get_characters():
    page = request.args.get('page', 1, type=int)

    try:
        response = requests.get(f"https://swapi.dev/api/people/?page={page}", timeout=5)
        response.raise_for_status()  # raises error if API fails

        data = response.json()
        characters = data.get('results', [])
        total = data.get('count', 0)
        total_pages = -(-total // 10)

        return render_template(
            'characters.html',
            characters=characters,
            page=page,
            total_pages=total_pages
        )

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Unable to fetch characters from Star Wars API"
        }), 503

# Fetch characters from Star Wars API with error handling

@app.route('/test-db')
def test_db():
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
        return jsonify({"status": "Database connected!"})

    except psycopg.Error:
        return jsonify({
            "error": "Database connection failed"
        }), 503

# Test databse connection with error handling

#got a new laptop test

def format_uptime(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"
# Convert time in seconds to hours and minutes

@app.route('/status')
def status():
    uptime_seconds = time.time() - START_TIME

    return jsonify({
        "status": "running",
        "version": APP_VERSION,
        "uptime": format_uptime(uptime_seconds),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
# Returns app info

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

        # Example query - adjust if your table name is different
        cur.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10;")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('leaderboard.html', scores=rows)

    except psycopg.Error as e:
        return jsonify({
            "error": "Unable to load leaderboard",
            "details": str(e)
        }), 503

if __name__ == '__main__':
    app.run(debug=True)
