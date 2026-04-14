from flask import Flask, jsonify, render_template, request, session, redirect, url_for
import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
_secret = os.getenv("SECRET_KEY", "insecure-default-do-not-use-in-production")
app.secret_key = _secret

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
#f this project

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
    except requests.RequestException:
        return jsonify({"error": "Unable to load leaderboard"}), 503


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'GET':
        try:
            page = random.randint(1, 8)
            response = requests.get(f"https://swapi.dev/api/people/?page={page}", timeout=5)
            response.raise_for_status()
            characters = response.json().get('results', [])
            character = random.choice(characters)

            homeworld_name = "Unknown"
            if character.get('homeworld'):
                hw = requests.get(character['homeworld'], timeout=5)
                hw.raise_for_status()
                homeworld_name = hw.json().get('name', 'Unknown')

            species_name = "Unknown"
            if character.get('species'):
                sp = requests.get(character['species'][0], timeout=5)
                sp.raise_for_status()
                species_name = sp.json().get('name', 'Unknown')

        except requests.RequestException:
            return render_template('error.html', message="Could not load quiz from SWAPI"), 503

        clues = [
            ["Homeworld", homeworld_name],
            ["Species", species_name],
            ["Gender", character.get('gender', 'Unknown')],
            ["Height", character.get('height', 'Unknown') + " cm"],
            ["Films appeared in", str(len(character.get('films', [])))],
        ]

        session['character_name'] = character['name']
        session['clues'] = clues
        session['clues_shown'] = 1
        session['state'] = 'playing'

        return render_template('quiz.html', clues=[clues[0]], clues_shown=1, state='playing')

    # POST — process guess
    if 'character_name' not in session:
        return redirect(url_for('quiz'))

    guess = request.form.get('guess', '').strip()
    character_name = session.get('character_name')
    clues = session.get('clues', [])
    clues_shown = session.get('clues_shown', 1)

    if guess.lower() == character_name.lower():
        score = 6 - clues_shown
        session['score'] = score
        session['state'] = 'correct'
        return render_template(
            'quiz.html',
            clues=clues[:clues_shown],
            clues_shown=clues_shown,
            state='correct',
            score=score,
            character_name=character_name
        )

    if clues_shown < 5:
        clues_shown += 1
        session['clues_shown'] = clues_shown
        return render_template(
            'quiz.html',
            clues=clues[:clues_shown],
            clues_shown=clues_shown,
            state='playing',
            wrong=True
        )

    session['state'] = 'gameover'
    return render_template(
        'quiz.html',
        clues=clues,
        clues_shown=clues_shown,
        state='gameover',
        character_name=character_name
    )


@app.route('/quiz/submit', methods=['POST'])
def quiz_submit():
    if session.get('state') != 'correct':
        return redirect(url_for('quiz'))

    username = request.form.get('username', '').strip()
    if not username:
        return render_template('error.html', message="Username cannot be empty"), 400

    score = session.get('score', 0)

    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/Leaderboard",
            headers={**_supabase_headers(), "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"name": username, "score": score},
            timeout=5
        )
        response.raise_for_status()
    except requests.RequestException:
        return render_template('error.html', message="Could not save score. Please try again."), 503

    session.clear()
    return redirect(url_for('leaderboard'))


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

#
if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
