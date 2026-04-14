# Team Collaboration Log

## Team & Roles

**Team size:** 4

1. **Liam (me)**
   - Deployment setup (Issue #15)
   - Quiz page (Issue #12 — originally Evan's, reassigned mid-sprint)
   - Compare/voting page
   - Logging (Issue #11 — deferred on purpose to avoid merge conflicts)
   - Merge conflict resolution and general Git troubleshooting

2. **Evan**
   - Tests (Issue #12)
   - Started the quiz page before it was handed over to me
   - Code review and testing support

3. **Andrew**
   - `/status` endpoint (Issue #8)
   - Error handling across routes (Issue #10)
   - Leaderboard page

4. **Adam**
   - Documentation (Issue #6)
   - Planets page
   - README

---

## Tools & Practices

### GitHub Issues

All work was tracked as GitHub Issues and linked to the PR that closed them.

Key issues:
- #6 — Documentation
- #8 — `/status` route
- #10 — Error handling
- #11 — Logging (deferred until all pages were merged)
- #12 — Tests
- #15 — Deployment config

### Project Board

We used a GitHub Projects Kanban board with four columns: **To Do**, **In Progress**, **Review**, and **Done**. Issues moved across as work progressed.

### Pull Request Workflow

- Every feature was built on its own branch.
- A PR had to be opened before merging to `master`.
- CI had to pass before the merge was allowed.
- PR titles and descriptions were kept clear.

**Example PRs:**

1. **Compare page** (`Compare-Page` → `master`) — character voting with 10 pre-set matchups, a new database table for votes, templates and CSS.
2. **Quiz page** (`appbroken` → `master`) — progressive clue system (5 clues per character), session-based game state, scoring (6 minus clues shown), leaderboard integration.
3. **Planets page** (Adam's branch → `master`) — SWAPI planets integration, pagination, template and styling.

### Review Process

Peer reviews were encouraged but not strictly enforced because of tight schedules. CI acted as the automatic gate, and the team focused on shipping working code within the deadline.

---

## Communication & Coordination

Most communication happened asynchronously through comments on GitHub issues and PRs. We didn't run formal sprint meetings — people picked up tasks based on when they were free.

Technical disagreements were worked out in issue comments. Merge conflicts were usually handled by whoever hit them, with help from the rest of the team when needed. The biggest recurring problem was conflicts between the new REST API code and the old `psycopg` code.

### Reassigning the Quiz Page

The quiz page was originally Evan's (Issue #12) but was handed to me partway through. We had to check who was doing what to avoid duplicate work. The lesson: confirm who currently owns a task before acting on an older plan.

### Deferring the Logging Task

Issue #11 (Logging) was held back on purpose. Adding logging would have touched every route, which would have caused merge conflicts across every open feature branch. The plan was to wait until everyone else had merged their pages, then add logging last. This turned out to be the right call.

---

## Version Control Evidence

### Branches in use
- `master` — main production branch
- `quiz-page` — my quiz feature
- `appbroken` — my conflict resolution branch
- `Compare-Page` — my voting feature
- Plus branches from the rest of the team for their own pages

### Example commits (mine)
- "add quiz page with progressive clues and scoring"
- "connect quiz to leaderboard via Supabase"
- "add compare page with character voting"
- "resolve conflicts - use clean REST API version"
- "fix: correct test structure for pytest"
- "add planets.html to git"

Commits were kept small and descriptive, with multiple commits per feature so the history shows the logical progression. Force pushes were only used on personal feature branches.

---

## Challenges & Lessons

### Technical

**1. Merge conflict hell**
Repeated conflicts between the REST API refactor and the old `psycopg` code led to several failed merge attempts. Fixed by using `git merge --abort` and resolving the conflicts through GitHub's web editor instead of locally. Lesson: sometimes the web UI is easier than fighting it on the command line.

**2. CI test failures**
Tests kept failing with "collected 0 items". The problem turned out to be the filename — `tests.py` instead of `test_app.py`. Pytest has specific naming rules for test discovery, and ours didn't match.

**3. Templates not deploying**
`planets.html` showed up in the folder but wasn't actually tracked by Git. `git ls-files` confirmed it was missing. Fix was a straight `git add`. Lesson: a file being in the directory doesn't mean it's in the repo.

**4. Database approach**
The `psycopg` direct connection and the Supabase REST API were fighting each other. We moved entirely to the REST API to keep the codebase simpler and easier for the rest of the team to follow. Sometimes simplifying beats optimising.

### What worked
- GitHub Issues for tracking
- Feature branches kept `master` stable
- Auto-deploy from `master` made iteration quick
- Async work fitted everyone's schedules

### What could be better
- Deciding on the database approach (psycopg vs REST) earlier
- More consistent PR reviews instead of relying on CI
- Clearer communication when tasks got reassigned
- Setting up the test framework earlier to avoid late-stage blockers

---

## Team Metrics

### Pull Requests
Every member authored at least 2 substantive PRs (the assignment requirement). I opened 4+ across quiz, compare, deployment, and conflict resolution. Overall distribution across the team was fairly balanced.

### Issues
6 major issues tracked and completed. One (logging) was intentionally deferred for workflow reasons.

### Code contributions
Work was split across frontend (HTML/CSS templates), backend (Flask routes, database integration, error handling), and infrastructure (CI/CD and deployment).

### Timeline
- **Week 1–2:** Repo setup and basic routes
- **Week 3:** Characters and planets pages
- **Week 4:** Quiz and compare/voting features
- **Week 5:** Deployment and CI/CD setup
- **Week 6:** Bug fixes, merge conflict resolution, final deployment

---

## Links & Evidence

- **Repository:** [https://github.com/liamproudford/AAEL]
- **Live deployment:** [Render URL] — auto-deploys from `master`
- **Key PRs:** Compare page, quiz page, planets page
- **Issue tracker:** [GitHub Issues link] / [GitHub Projects board link]

---

## Conclusion

Despite the merge conflict issues, CI hiccups, and deployment problems, the team shipped a working app that meets all the assignment requirements:

✓ Two data sources integrated (SWAPI + Supabase)
✓ Multiple features (quiz, voting, leaderboard, character/planet browsing)
✓ Health and status endpoints
✓ CI/CD pipeline with automated tests and deployment
✓ PR workflow with branch protection
✓ Issue tracking and project board
✓ 12-factor config using environment variables
✓ Error handling across all routes

The main takeaways from the collaboration side were around Git workflows, managing dependencies between tasks, and being clear about who's working on what when the team is distributed and async.