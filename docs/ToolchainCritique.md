# Toolchain Critique

## Summary

This document looks at the tech stack we picked for the project — what worked, what didn't, and what we'd do differently next time. Overall the stack did the job and we shipped a working app that met the assignment requirements, but there were a few pain points worth flagging for future projects.

---

## 1. What Worked Well

### Flask + Python

**Strengths**
- Easy to get started with, even for team members without much web dev experience.
- Good docs and a big community, so problems were easy to search.
- Jinja2 templating let us reuse layouts across pages instead of copy-pasting HTML.
- The `requests` library made calling SWAPI straightforward.

**Evidence**
- All four of us were able to add routes and templates without much trouble.
- The quiz feature (which has the most complex session logic) was built in about two days.
- The characters and planets pages barely needed any debugging.

**Verdict:** ✅ Strong choice for this project.

### Supabase

**Strengths**
- REST API out of the box, so no ORM or raw SQL needed.
- Free tier was enough for everything we did.
- The dashboard made it easy to check data and tweak tables.
- Setup took about ten minutes.

**Challenges**
- We wasted time at the start because the team wasn't clear on whether to use `psycopg` or the REST API.
- Had to refactor mid-project once we agreed on the REST API.
- Error messages are less useful than what you'd get from direct SQL.

**Verdict:** ✅ Good choice, but we should have agreed on the approach earlier.

### GitHub + GitHub Actions

**Strengths**
- Issues, PRs, and CI/CD all in one place.
- Free for public repos.
- Industry standard, so the experience is transferable.
- The workflow YAML lives in the repo, so it's version-controlled.

**Challenges**
- CI runs took 2–3 minutes, which felt slow when you're pushing often.
- No SSH into runners on the free tier, so debugging a broken build was painful.
- Failing tests blocked merges and occasionally needed a manual bypass.

**Verdict:** ✅ Fine for a student project. The slow builds are a fair trade-off for free.

### Render

**Strengths**
- Connected GitHub, clicked deploy, and it worked.
- Auto-deploy from `master` meant no manual release steps.
- Free tier, no card needed.
- Environment variables are easy to manage in the dashboard.

**Challenges**
- A caching issue meant templates in GitHub weren't showing up in production, and we eventually had to delete and recreate the service to clear it.
- No shell access on the free tier, so we couldn't inspect the deployed files.
- Cold starts on the free tier caused 50+ second delays on the first request after idle.

**Verdict:** ⚠️ Worked, but annoying. Would look at alternatives next time.

---

## 2. What We Would Change

### Testing

**Problem**
Tests were added too late. We hit pytest discovery issues (`tests.py` vs `test_app.py`), struggled with `@patch`, and the test suite ended up being a blocker instead of a safety net.

**Better approach**
- Set up the test framework on day 1 with a couple of example tests already passing.
- Run `pytest` locally before pushing.
- Keep tests simple — basic route checks, no fancy fixtures.
- Skip coverage reporting until the basics are stable.

**Alternative:** use `unittest` (built into Python) to sidestep pytest's configuration quirks.

### Database Decision

**Problem**
Half the team was using `psycopg`, the other half was using Supabase's REST API. This caused repeated merge conflicts and a forced refactor mid-project.

**Better approach**
Make one architectural decision in week 1, write it down in the README, and stick to it. This would have saved us at least 4 hours.

### Git Workflow

**Problem**
Feature branches lived too long and drifted from `master`, so conflicts got worse the longer we waited. Some of the team weren't confident resolving conflicts either.

**Better approach**
- Smaller, more frequent merges — days, not weeks.
- Pull from `master` daily to stay in sync.
- Pair up for tricky conflict resolution so everyone learns how to handle it.

**Alternative:** use `git rebase` instead of `git merge` for a cleaner history.

### Deployment Platform

**Problem**
Render's caching forced a full service rebuild, the free tier gave us no way to debug, and cold starts made the live demo feel sluggish.

**Better approach**
- **Railway or Fly.io** — similar ease, better debugging on free tiers.
- **Heroku** — more reliable but not free.
- **Self-hosted Docker on a university VM** — more setup but more learning.

The frustration probably cost us more time than a $5/month paid tier would have.

---

## 3. Risks & Mitigations

### Risk 1: SWAPI goes down

**Likelihood:** Medium — it's a free, community-run API.
**Impact:** High — the characters and planets pages would break.

**What we did**
- Error pages instead of crashes.
- 5 second timeouts so the app doesn't hang.
- `/status` endpoint reports SWAPI health separately.

**What we'd add**
- A cache (Redis or local file) so recent responses are still usable.
- Static fallback data as a backup.
- Awareness of rate limits, even though SWAPI doesn't document any.

### Risk 2: Supabase goes down

**Likelihood:** Low — Supabase has a solid uptime track record.
**Impact:** Medium — the quiz still runs, but scores and votes can't be saved.

**What we did**
- Database check on `/status`.
- Try/except blocks return 503 instead of crashing.
- Friendly error messages for users.

**What we'd add**
- Connection pooling to avoid opening a new connection per request.
- Retry logic (2–3 attempts before failing).
- A circuit breaker to stop hammering a dead database.

### Risk 3: Leaking secrets

**Likelihood:** Medium — easy mistake for beginners.
**Impact:** Critical — a public repo means anyone could read our database if a key leaked.

**What we did**
- `.env` in `.gitignore`.
- `.env.example` with placeholder values only.
- GitHub Actions secrets for CI.
- Render env vars for production.

**What we'd add**
- A pre-commit hook to block any commit containing `SUPABASE_KEY=` or `SECRET_KEY=`.
- GitHub's built-in secret scanning.
- Rotating keys regularly as best practice.

### Risk 4: Broken CI blocks everyone

**Likelihood:** High — we hit this more than once.
**Impact:** Medium — there's a bypass, but it defeats the point of CI.

**What we did**
- Bypass for emergencies.
- Multiple team members able to debug the pipeline.

**What we'd add**
- Split lint and test into separate jobs so one failing doesn't block the other.
- Matrix testing across Python versions.
- Cache pip dependencies to bring CI runs from 3 minutes down to under 1.

### Risk 5: Merge conflicts killing momentum

**Likelihood:** High — definitely happened to us.
**Impact:** High — 4+ hours lost and a noticeable hit to morale.

**What we did**
- `git merge --abort` and retry.
- Used the GitHub web editor for simpler conflicts.
- Force pushes on personal branches when needed.

**What we'd add**
- Pulling from `master` daily.
- Smaller commits so conflicts are easier to read.
- Announcing big refactors in advance so the team can merge before the change lands.

---

## 4. Alternatives We Considered

### Django instead of Flask

**Pros:** built-in admin panel, ORM included, more opinionated structure.
**Cons:** steeper learning curve, more boilerplate, overkill for this project.
**Decision:** Flask was the right call for our scope and experience level.

### MongoDB instead of PostgreSQL

**Pros:** schema-less, native JSON, free tier on MongoDB Atlas.
**Cons:** no relational queries, less familiar, and the assignment required PostgreSQL anyway.
**Decision:** PostgreSQL was the right call and we learned more SQL because of it.

### Docker Compose for local dev

**Pros:** identical environment for every team member, one command to spin everything up, closer to production.
**Cons:** learning curve, Windows/WSL2 friction, overkill for a small Flask app.
**Decision:** In hindsight, we should have done this. It would have prevented the "works on my machine" problems and made onboarding quicker.

---

## 5. Lessons for Future Projects

### Technical
1. Agree on architecture early — database, deployment, code structure.
2. Set up tests before writing production code.
3. Merge to `master` often to avoid conflict buildup.
4. Use Docker so every environment is the same.

### Process
1. Communicate often, even async — a daily update would have stopped duplicate work.
2. Write down *why* decisions were made, not just how to run the app.
3. Pair up on blockers.
4. Time-box debugging. If you're stuck for 30 minutes, ask for help or work around it.

### Collaboration
1. Be clear about who owns what, and communicate reassignments explicitly.
2. Human code reviews catch things CI can't.
3. Celebrate small wins — every merged PR is progress.

---

## 6. Cost vs Benefit

### Time vs Learning

**Good ROI**
- CI/CD setup (≈2 hours) → industry-standard skill, automatic quality checks.
- Supabase setup (≈1 hour) → hands-on with cloud databases.
- Error handling (≈3 hours) → better UX, real-world resilience patterns.

**Poor ROI**
- Merge conflicts (≈4 hours) → avoidable with better workflow.
- Template deployment debugging (≈3 hours) → platform-specific, not transferable.
- Test framework troubleshooting (≈2 hours) → config issue, not actual testing skill.

**Summary:** the time was worth it overall, but roughly 9 hours went on avoidable problems.

### Tool Costs

**Free tier services used**
- GitHub (unlimited public repos)
- GitHub Actions (2,000 CI minutes/month)
- Render (750 hours/month with cold starts)
- Supabase (500MB, 50,000 requests/month)

**Total cost: €0**

**Trade-offs we accepted**
- Slow CI builds.
- Cold starts on Render.
- No real support beyond docs and Stack Overflow.

**Worth paying for ($5–10/month)**
- Render Pro: no cold starts, more RAM.
- Supabase paid tier: more storage and better performance.

---

## 7. Recommendations for Similar Projects

### For student teams with no budget
- Flask + Python
- Supabase
- GitHub + GitHub Actions
- Railway or Fly.io (better free debugging than Render)
- Docker Compose for local dev

### For production apps with a budget
- FastAPI instead of Flask (faster, auto-generated API docs)
- Managed PostgreSQL (AWS RDS or DigitalOcean) for more control
- CircleCI for faster builds and better caching
- Heroku or AWS Elastic Beanstalk for reliable deployment
- Sentry for error tracking

### Universal advice
1. Set up CI/CD before writing production code.
2. Use Docker even on small projects.
3. Automate anything you do more than once.
4. Add logging and health checks before you need them.
5. Keep it simple — fewer technologies, less complexity.

---

## Conclusion

The toolchain we picked did what it needed to. Flask, Supabase, GitHub Actions, and Render were a reasonable fit for a four-person student team on a six-week deadline.

**Wins**
- Zero infrastructure cost.
- Fully automated CI/CD.
- Live deployment in the cloud.
- Proper version control and collaboration workflows.

**Losses**
- Template caching issues on Render.
- Time lost to merge conflicts.
- Late test framework causing blockers.

**Overall:** the tools themselves were fine. Most of the problems came from team process — not the tech. If we did this again we'd keep the same core stack but fix the workflow around Git, database decisions, and testing.

The wider lesson is that modern cloud platforms and CI/CD tools genuinely do let a small team build and deploy a working application for nothing. That's a pretty big shift in what's possible, and worth appreciating.