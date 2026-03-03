
from flask import Flask, jsonify
import requests
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/characters')
def get_characters():
    response = requests.get("https://swapi.dev/api/people/")
    data = response.json()
    return jsonify(data)

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

if __name__ == '__main__':
    app.run(debug=True)


