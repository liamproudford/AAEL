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

MATCHUPS = [
    ("Luke Skywalker", "Darth Vader"),
    ("Han Solo", "Lando Calrissian"),
    ("Yoda", "Palpatine"),
    ("Obi-Wan Kenobi", "Anakin Skywalker"),
    ("Chewbacca", "Boba Fett"),
    ("Leia Organa", "Padmé Amidala"),
    ("R2-D2", "C-3PO"),
    ("Qui-Gon Jinn", "Mace Windu"),
    ("Jabba Desilijic Tiure", "Greedo"),
    ("Wedge Antilles", "Biggs Darklighter"),
]


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


@app.route('/planets')
def get_planets():
    page = request.args.get('page', 1, type=int)
    try:
        response = requests.get(f"https://swapi.dev/api/planets/?page={page}", timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return render_template('error.html', message="Could not fetch planets from SWAPI"), 503
    planets = data.get('results', [])
    total = data.get('count', 0)
    total_pages = -(-total // 10)
    return render_template('planets.html', planets=planets, page=page, total_pages=total_pages)


@app.route('/compare')
def compare():
    if 'voted_matchups' not in session:
        session['voted_matchups'] = []
    voted = session['voted_matchups']
    if len(voted) >= 10:
        return redirect(url_for('compare_stats'))
    matchup_id = next(i for i in range(10) if i not in voted)
    character1, character2 = MATCHUPS[matchup_id]
    progress = f"Matchup {len(voted) + 1} of 10"
    return render_template('compare.html', matchup_id=matchup_id,
                           character1=character1, character2=character2, progress=progress)


@app.route('/compare/vote', methods=['POST'])
def compare_vote():
    matchup_id = int(request.form.get('matchup_id'))
    winner_name = request.form.get('winner_name')
    character1, character2 = MATCHUPS[matchup_id]

    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/character_votes",
            headers={**_supabase_headers(), "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"matchup_id": matchup_id, "character1_name": character1,
                  "character2_name": character2, "winner_name": winner_name},
            timeout=5
        ).raise_for_status()

        rows = requests.get(
            f"{SUPABASE_URL}/rest/v1/character_votes?matchup_id=eq.{matchup_id}&select=winner_name",
            headers=_supabase_headers(),
            timeout=5
        ).json()
    except requests.RequestException:
        return render_template('error.html', message="Could not save vote. Please try again."), 503

    vote_counts = {character1: 0, character2: 0}
    for row in rows:
        name = row.get('winner_name')
        if name in vote_counts:
            vote_counts[name] += 1

    total_votes = sum(vote_counts.values())
    char1_votes = vote_counts[character1]
    char2_votes = vote_counts[character2]
    char1_pct = round(char1_votes / total_votes * 100) if total_votes else 0
    char2_pct = round(char2_votes / total_votes * 100) if total_votes else 0

    if 'voted_matchups' not in session:
        session['voted_matchups'] = []
    session['voted_matchups'].append(matchup_id)
    session.modified = True

    return render_template('compare_results.html', winner_name=winner_name,
                           character1=character1, character2=character2,
                           char1_votes=char1_votes, char2_votes=char2_votes,
                           char1_pct=char1_pct, char2_pct=char2_pct, total_votes=total_votes)


@app.route('/compare/stats')
def compare_stats():
    try:
        rows = requests.get(
            f"{SUPABASE_URL}/rest/v1/character_votes?select=matchup_id,winner_name",
            headers=_supabase_headers(),
            timeout=5
        ).json()
    except requests.RequestException:
        return render_template('error.html', message="Could not load stats."), 503

    matchup_results = []
    for idx, (char1, char2) in enumerate(MATCHUPS):
        vote_counts = {char1: 0, char2: 0}
        for row in rows:
            if row.get('matchup_id') == idx and row.get('winner_name') in vote_counts:
                vote_counts[row['winner_name']] += 1
        total = sum(vote_counts.values())
        if total > 0:
            char1_pct = round(vote_counts[char1] / total * 100)
            char2_pct = round(vote_counts[char2] / total * 100)
            winner = char1 if vote_counts[char1] >= vote_counts[char2] else char2
            winner_pct = max(char1_pct, char2_pct)
        else:
            char1_pct = char2_pct = winner_pct = 0
            winner = "No votes yet"
        matchup_results.append({
            'matchup_num': idx + 1, 'character1': char1, 'character2': char2,
            'char1_votes': vote_counts[char1], 'char2_votes': vote_counts[char2],
            'char1_pct': char1_pct, 'char2_pct': char2_pct,
            'winner': winner, 'winner_pct': winner_pct, 'total_votes': total
        })

    valid = [m for m in matchup_results if m['total_votes'] > 0]
    most_dominant = max(valid, key=lambda x: x['winner_pct']) if valid else None
    closest = min(valid, key=lambda x: abs(50 - x['winner_pct'])) if valid else None

    return render_template('compare_stats.html', matchup_results=matchup_results,
                           most_dominant=most_dominant, closest=closest)


@app.route('/compare/reset')
def compare_reset():
    session['voted_matchups'] = []
    return redirect(url_for('compare'))


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
