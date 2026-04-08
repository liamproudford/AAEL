
from flask import Flask, jsonify, render_template, request, session, redirect
import requests
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Add this right after:
if not app.secret_key or app.secret_key == "dev-secret-key":
    import secrets
    app.secret_key = secrets.token_hex(32)


# 10 pre-defined Star Wars matchups
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


@app.route('/compare')
def compare():
    # Initialize voted matchups in session if not exists
    if 'voted_matchups' not in session:
        session['voted_matchups'] = []

    voted = session['voted_matchups']

    # If user has voted on all 10, redirect to stats
    if len(voted) >= 10:
        return redirect('/compare/stats')

    # Find next matchup they haven't voted on
    matchup_id = None
    for i in range(10):
        if i not in voted:
            matchup_id = i
            break

    character1, character2 = MATCHUPS[matchup_id]
    progress = f"Matchup {len(voted) + 1} of 10"

    return render_template('compare.html',
                           matchup_id=matchup_id,
                           character1=character1,
                           character2=character2,
                           progress=progress
                           )


@app.route('/compare/vote', methods=['POST'])
def compare_vote():
    matchup_id = int(request.form.get('matchup_id'))
    winner_name = request.form.get('winner_name')

    character1, character2 = MATCHUPS[matchup_id]

    # Insert vote into database
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

        cur.execute("""
                    INSERT INTO character_votes (matchup_id, character1_name, character2_name, winner_name)
                    VALUES (%s, %s, %s, %s)
                    """, (matchup_id, character1, character2, winner_name))
        conn.commit()

        # Get vote counts for this matchup
        cur.execute("""
                    SELECT winner_name, COUNT(*)
                    FROM character_votes
                    WHERE matchup_id = %s
                    GROUP BY winner_name
                    """, (matchup_id,))

        results = cur.fetchall()
        cur.close()
        conn.close()

        # Calculate percentages
        vote_counts = {character1: 0, character2: 0}
        for winner, count in results:
            vote_counts[winner] = count

        total_votes = sum(vote_counts.values())
        char1_votes = vote_counts[character1]
        char2_votes = vote_counts[character2]
        char1_pct = round((char1_votes / total_votes * 100)) if total_votes > 0 else 0
        char2_pct = round((char2_votes / total_votes * 100)) if total_votes > 0 else 0

        # Mark this matchup as voted
        if 'voted_matchups' not in session:
            session['voted_matchups'] = []
        session['voted_matchups'].append(matchup_id)
        session.modified = True

        return render_template('compare_results.html',
                               winner_name=winner_name,
                               character1=character1,
                               character2=character2,
                               char1_votes=char1_votes,
                               char2_votes=char2_votes,
                               char1_pct=char1_pct,
                               char2_pct=char2_pct,
                               total_votes=total_votes
                               )

    except Exception as e:
        return jsonify({"error": str(e)}), 503


@app.route('/compare/stats')
def compare_stats():
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

        # Get all matchup results
        matchup_results = []
        for idx, (char1, char2) in enumerate(MATCHUPS):
            cur.execute("""
                        SELECT winner_name, COUNT(*)
                        FROM character_votes
                        WHERE matchup_id = %s
                        GROUP BY winner_name
                        """, (idx,))

            results = cur.fetchall()
            vote_counts = {char1: 0, char2: 0}
            for winner, count in results:
                vote_counts[winner] = count

            total = sum(vote_counts.values())
            if total > 0:
                char1_pct = round((vote_counts[char1] / total * 100))
                char2_pct = round((vote_counts[char2] / total * 100))
                winner = char1 if vote_counts[char1] > vote_counts[char2] else char2
                winner_pct = max(char1_pct, char2_pct)
            else:
                char1_pct = char2_pct = 0
                winner = "No votes yet"
                winner_pct = 0

            matchup_results.append({
                'matchup_num': idx + 1,
                'character1': char1,
                'character2': char2,
                'char1_votes': vote_counts[char1],
                'char2_votes': vote_counts[char2],
                'char1_pct': char1_pct,
                'char2_pct': char2_pct,
                'winner': winner,
                'winner_pct': winner_pct,
                'total_votes': total
            })

        cur.close()
        conn.close()

        # Find most dominant and closest matchup
        valid_matchups = [m for m in matchup_results if m['total_votes'] > 0]
        most_dominant = max(valid_matchups, key=lambda x: x['winner_pct']) if valid_matchups else None
        closest = min(valid_matchups, key=lambda x: abs(50 - x['winner_pct'])) if valid_matchups else None

        return render_template('compare_stats.html',
                               matchup_results=matchup_results,
                               most_dominant=most_dominant,
                               closest=closest
                               )

    except Exception as e:
        return jsonify({"error": str(e)}), 503


@app.route('/compare/reset')
def compare_reset():
    session['voted_matchups'] = []
    return redirect('/compare')

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
