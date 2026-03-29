# Personal Finance Tracker API

A secure REST API for tracking personal income and expenses, built with Flask, PostgreSQL, and JWT authentication.

## Features
- JWT Authentication (register, login, protected routes)
- Add income and expense transactions
- Filter transactions by type and category
- Monthly financial summary (income, expenses, savings)
- 15 pytest unit tests — 100% passing
- CI/CD pipeline via GitHub Actions

## Tech Stack
Python · Flask · PostgreSQL · JWT · bcrypt · pytest · GitHub Actions

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | ❌ | Health check |
| POST | /register | ❌ | Create account |
| POST | /login | ❌ | Get JWT token |
| POST | /transactions | ✅ | Add transaction |
| GET | /transactions | ✅ | Get all transactions |
| GET | /transactions/summary | ✅ | Monthly summary |
| DELETE | /transactions/<id> | ✅ | Delete transaction |

## Setup
1. Clone the repo
2. Copy `config.example.py` to `config.py` and fill in credentials
3. Install: `pip install flask psycopg2-binary pytest pyjwt bcrypt`
4. Create tables: `python setup_db.py`
5. Run API: `python app.py`
6. Run tests: `python -m pytest test_app.py -v`
```

---

**Step 2 — Create `requirements.txt`:**
```
flask
psycopg2-binary
pytest
pyjwt
bcrypt