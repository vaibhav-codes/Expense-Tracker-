# Spec: Login and Logout

## Overview
Implement session-based authentication for Spendly: upgrade the existing `GET /login` stub into a full login form that validates credentials against the `users` table and starts a Flask session, and implement the `GET /logout` stub to clear that session and bring user back to landing page. This is the step that turns Spendly from a collection of public pages into an app with an authenticated user context — every following step (profile, expenses) depends on knowing who is logged in.

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`)
- Step 02 — Registration (`create_user()`, users can already sign up with a hashed password)

## Routes
- `GET /login` — render login form — public (already exists as stub, upgrade it)
- `POST /login` — validate credentials, start session, redirect to a logged-in landing point — public
- `GET /logout` — clear session, redirect to `/login` — logged-in (stub, upgrade it per Step 3)

## Database changes
No new tables or columns. The existing `users` table (id, name, email, password_hash, created_at) covers all requirements.

A new DB helper must be added to `database/db.py`:
- `get_user_by_email(email)` — parameterized `SELECT` against `users` by email, returns a `sqlite3.Row` or `None`. Used to look up the row so `app.py` can verify the password hash with `werkzeug.security.check_password_hash`.

## Templates
- **Modify**: `templates/login.html`
  - Change the form `action="/login"` to `action="{{ url_for('login') }}"` (hardcoded URL currently violates CLAUDE.md conventions)
  - Keep `method="POST"`, keep existing `name="email"` / `name="password"` inputs — no changes needed there
  - The existing `{% if error %}` block can stay, but rely on `base.html`'s flash-message rendering (already wired up) for validation errors, consistent with `register.html`'s pattern from Step 02
- **Modify**: `templates/base.html`
  - Nav currently always shows "Sign in" / "Get started" links. Add a session-aware check (`{% if session.user_id %}`) so a logged-in user sees a "Logout" link (`url_for('logout')`) instead of "Sign in" / "Get started". This requires no route changes — `session` is available in Jinja by default.

## Files to change
- `app.py` — upgrade `login()` to handle `GET` and `POST`; upgrade `logout()` from placeholder string to real session-clearing logic; import `session` from `flask`
- `database/db.py` — add `get_user_by_email()` helper
- `templates/login.html` — fix hardcoded form action to use `url_for()`
- `templates/base.html` — make nav session-aware (show Logout when logged in)

## Files to create
None.

## New dependencies
No new dependencies. Uses `werkzeug.security.check_password_hash` (already installed via Step 02's `generate_password_hash` usage) and Flask's built-in `session`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use f-strings in SQL
- Passwords hashed with werkzeug — verify with `check_password_hash`, never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- On `POST /login` with a missing/unknown email or wrong password, flash a single generic error (e.g. "Invalid email or password") — do not reveal whether the email exists, and re-render the login form without redirecting
- On successful login, store at minimum `session["user_id"]` (and optionally `session["user_name"]`) — do not store the password or password hash in the session
- `GET /logout` must call `session.clear()` (or pop the relevant keys) then `flash` a confirmation message and `redirect` to `url_for('login')`
- Use `abort(405)` if an unsupported HTTP method reaches `/login`
- Use `url_for()` for every internal link — never hardcode URLs (fixes the existing hardcoded `/login` action)
- Do not implement route protection / `@login_required` for `/profile` or `/expenses/*` in this step — those stubs stay as-is until their own steps; this step only establishes the session mechanism

## Definition of done
- [ ] `GET /login` renders the login form without errors
- [ ] Submitting valid credentials (e.g. seeded `demo@spendly.com` / `demo123`) logs the user in and redirects away from `/login`
- [ ] After login, `session["user_id"]` is set and the nav in `base.html` shows a "Logout" link instead of "Sign in" / "Get started"
- [ ] Submitting an unknown email re-renders the login form with a generic "Invalid email or password" error, no session set
- [ ] Submitting a known email with the wrong password re-renders the login form with the same generic error, no session set
- [ ] Visiting `GET /logout` while logged in clears the session and redirects to `/login`
- [ ] After logout, the nav reverts to showing "Sign in" / "Get started"
- [ ] No plaintext password ever appears in `session` or is compared directly against `password_hash`
