# Local synthetic buyer demonstration

Use a reviewed release including audit PRs #66–68. Do not deploy this demonstration publicly or run its seed against production.

Requirements: Python 3.12 and Node 22+. Create a virtualenv, upgrade pip and install `backend/requirements.lock`. Run `npm ci` inside `frontend`. Run backend pytest from `backend`, and frontend test/lint/build from `frontend`.

From `backend`, set development environment variables:
- `APP_ENV=development`
- `DATABASE_URL=sqlite:///./buyer-demo.db` (a new dedicated file)
- `AUTH_SECRET_KEY`: a private random signing secret
- `NESTORA_DEMO_PASSWORD`: a private synthetic account password, at least 12 characters
- `EMAIL_PROVIDER=disabled`, `LLM_PROVIDER=mock`
- Empty `GOOGLE_API_KEY` and `GEMINI_API_KEY` for the offline demonstration

Run `python demo_seed.py`, then `python -m uvicorn main:app --host 127.0.0.1 --port 8001`. In another terminal, start Vite on loopback port 5175 with `VITE_API_BASE_URL=http://127.0.0.1:8001`. Visit `http://localhost:5175` and sign in as `buyer-demo@nestora.test` using the password you chose locally.

The seed creates two fictional workspaces, six fictional leads, two planned missions and two pending tasks. It refuses existing database files, production mode, non-SQLite storage, enabled email and a live generic model provider. It never overwrites data or sends external messages. Do not interpret demo records or fallback reports as customers, revenue or actual campaign results.

Verify workspace switching, CRM updates, dashboard/CEO access and persistence after restart. Explain placeholders, deterministic CEO behavior and mock/fallback AI. Live model/search/email, browser voice, mobile usability and PostgreSQL production behavior require separate controlled acceptance checks.

Detailed acquisition audit and handover materials are owner-review documents. No listing, deployment, transfer or credential changes are authorized by this demonstration guide.
