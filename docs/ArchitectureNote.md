# Architecture Note

## 1. System Context & Integration Points

### Overview
This is a Star Wars themed Flask web app. It pulls character and planet data from an external API and stores quiz scores and votes in a cloud database. Users can browse characters, play a guessing quiz, vote in matchups, and see a leaderboard.

### Data Sources

1. **SWAPI (Star Wars API)** — external HTTP API at `https://swapi.dev/api/`. Used for character, planet, and species data. Called live on each request.

2. **Supabase (PostgreSQL)** — cloud database with two tables, `Leaderboard` and `character_votes`. Accessed through Supabase's REST API. We originally used a direct `psycopg` connection but switched to the REST client because it was simpler and less error-prone.

### Request Flow

```
User Request
    ↓
Flask app (app.py)
    ↓
├─→ SWAPI  (characters, planets)
│      └─→ parse JSON → render template
│
└─→ Supabase REST API  (scores, votes)
       └─→ POST/GET → update UI
```

### Routes

**Main pages:**
- `GET /` — home page with navigation cards
- `GET /characters` — paginated character list from SWAPI
- `GET /planets` — paginated planet list from SWAPI
- `GET /quiz` — guess-the-character game with progressive clues
- `POST /quiz` — handle a guess
- `POST /quiz/submit` — save score to Supabase
- `GET /leaderboard` — top scores
- `GET /compare` — character voting matchups
- `POST /compare/vote` — record a vote
- `GET /compare/stats` — vote totals

**Health checks:**
- `GET /health` — returns 200 if SWAPI and Supabase are both reachable
- `GET /status` — more detailed check with error info

### Error Handling

Every external call is wrapped in try/except with a 5-second timeout. If something fails, the user gets a friendly error page instead of a crash. Database failures return a 503.

Example from the `/characters` route:

```python
try:
    response = requests.get(f"https://swapi.dev/api/people/?page={page}", timeout=5)
    response.raise_for_status()
    data = response.json()
except requests.RequestException:
    return render_template('error.html', message="Could not fetch characters from SWAPI"), 503
```

---

## 2. Branching Model & Git Workflow

We used trunk-based development with short-lived feature branches.

- `master` is the main branch and auto-deploys to Render.
- Features are built on branches like `quiz-page`, `Compare-Page`, `appbroken`, etc.
- Branches are merged into `master` through Pull Requests once CI passes.

### Workflow

1. Open a GitHub issue for the feature (e.g. Issue #11 — Logging).
2. Branch off `master`.
3. Build the feature locally.
4. Push and open a PR.
5. CI runs lint and tests automatically.
6. Review (where possible) and merge.
7. Render picks up the change and redeploys.

### Commits
Commit messages were kept descriptive, e.g. *"add quiz page with progressive clues"* or *"fix: resolve merge conflicts in app.py"*. Every team member made several meaningful PRs.

### Problems we hit
The biggest issue was merge conflicts between the new REST API code and the old `psycopg` code. We fixed these with `git merge --abort` and resolved the conflicts through GitHub's web editor.

---

## 3. CI/CD Pipeline

### Continuous Integration (GitHub Actions)

Defined in `.github/workflows/ci.yml`. Runs on every push and every PR to `master`.

Steps:

1. Check out the code and set up Python 3.11.
2. Install dependencies from `requirements.txt`.
3. Lint with `ruff check .`.
4. Run tests with `pytest --cov=app tests/`.
5. Report pass/fail back to the PR. A failing build blocks the merge.

CI environment variables:

```yaml
env:
  SECRET_KEY: ci-test-secret
  SUPABASE_URL: https://placeholder.supabase.co
  SUPABASE_KEY: placeholder-key
```

### Continuous Deployment (Render)

- **Source:** GitHub `master` branch
- **Build:** `pip install -r requirements.txt`
- **Start:** `gunicorn app:app`
- **Auto-deploy:** on every push to `master`

Production environment variables (set in the Render dashboard):
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY`
- `FLASK_DEBUG` (set to `false`)

### Deployment flow

```
Push to master
    ↓
GitHub webhook → Render
    ↓
Render pulls code, installs deps, starts gunicorn
    ↓
App live at the Render URL
```

### Config Management

We followed the 12-factor approach: no secrets in the repo, everything in environment variables. A `.env.example` file is included for local setup:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
SECRET_KEY=a-long-random-secret-key
FLASK_DEBUG=false
```

---

## 4. Technology Stack

**Flask** — lightweight and easy to pick up, which suited the team's experience level. Comes with Jinja2 templating and built-in session handling for the quiz state.

**Supabase** — gives us a PostgreSQL database with a REST API out of the box, so we didn't have to set up an ORM or write raw SQL. Free tier covers everything we need.

**SWAPI** — free, public, no auth, clean JSON. A good fit for demonstrating API integration.

**GitHub Actions** — built into GitHub, free for public repos, and the config lives in the repo itself so it's version-controlled.

**Render** — free tier, deploys straight from GitHub, simple env var setup, and no card needed.

---

## 5. Security

**Secrets:** all credentials live in environment variables. Nothing sensitive is committed. CI uses GitHub Actions secrets; production uses Render's env var settings.

**Input handling:** Flask sanitises form input, and because we use Supabase's REST API rather than raw SQL, queries are parameterised and safe from SQL injection. Rate limiting is handled upstream by SWAPI and Supabase.

**Sessions:** Flask sessions are signed with a secret key, cookies are HTTP-only by default, and quiz state is kept server-side.

---

## 6. Future Improvements

**Scalability**
- Cache SWAPI responses (e.g. Redis) to reduce external calls.
- Add connection pooling.
- Serve static files through a CDN.

**Observability**
- Structured logging with request IDs.
- Application performance monitoring.
- Error tracking with something like Sentry.

**Testing**
- More test coverage beyond basic route tests.
- Integration tests against a real database.
- End-to-end tests with Selenium.

**Features**
- User accounts and authentication.
- Live leaderboard updates via WebSockets.
- Admin dashboard for managing content.