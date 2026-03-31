# Smart Expense Tracker API

A production-style REST API built with **Python · FastAPI · PostgreSQL · SQLAlchemy · Pytest**.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        HTTP Clients                         │
│              (Browser / curl / Swagger UI)                  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
│                         main.py                             │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────────────┐  │
│  │  /expenses       │        │  /reports                │  │
│  │  POST   (create) │        │  GET /summary            │  │
│  │  POST   (bulk)   │        │  GET /weekly             │  │
│  │  GET    (list)   │        │  GET /monthly?month&year │  │
│  │  GET    /{id}    │        │  GET /yearly?year        │  │
│  │  PATCH  /{id}    │        └──────────────────────────┘  │
│  │  DELETE /{id}    │                                       │
│  └──────────────────┘                                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Pydantic Schemas  (schemas.py)         │   │
│  │   Request validation · Response serialisation       │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ Validated Python objects
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    CRUD Layer  (crud.py)                    │
│      Pure database functions — no HTTP concerns here        │
│   create · bulk_create · get · list · update · delete       │
│   summary_by_shop · weekly_total · monthly_total · yearly   │
└────────────────────────────┬────────────────────────────────┘
                             │ SQLAlchemy ORM queries
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer  (models.py)                │
│                                                             │
│   Expense                                                   │
│   ├── id          INTEGER  PK                               │
│   ├── description VARCHAR  NOT NULL                         │
│   ├── amount      FLOAT    NOT NULL                         │
│   └── date        DATE     NOT NULL                         │
└────────────────────────────┬────────────────────────────────┘
                             │ SQLAlchemy Engine
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL  (database.py)                      │
│              DATABASE_URL env variable                      │
└─────────────────────────────────────────────────────────────┘
```

### Layer responsibilities

| File | Role |
|------|------|
| `main.py` | HTTP routing, request/response handling, status codes |
| `schemas.py` | Pydantic models — validates inputs, serialises outputs |
| `crud.py` | All DB operations; no FastAPI imports |
| `models.py` | SQLAlchemy ORM table definitions |
| `database.py` | Engine, session factory, `get_db` dependency |

---

## Project Structure

```
expense_tracker/
├── __init__.py
├── main.py          ← FastAPI app + routes
├── database.py      ← DB connection & session
├── models.py        ← SQLAlchemy ORM models
├── schemas.py       ← Pydantic request/response schemas
├── crud.py          ← Pure DB operations
├── requirements.txt
├── README.md
└── tests/
    ├── __init__.py
    ├── conftest.py          ← Fixtures: in-memory SQLite, TestClient
    ├── test_expenses.py     ← CRUD endpoint tests
    └── test_reports.py      ← Report endpoint tests
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ running locally

### 1 — Clone / copy the project

```bash
# Place the expense_tracker/ folder wherever you want
cd path/to/parent_folder
```

### 2 — Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 3 — Install dependencies

```bash
pip install -r expense_tracker/requirements.txt
```

### 4 — Create the PostgreSQL database

```sql
-- In psql or any PG client
CREATE DATABASE expense_tracker;
```

### 5 — Configure the database URL

Set the `DATABASE_URL` environment variable before running:

```bash
export DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/expense_tracker"
```

Or create a `.env` file in the project root (add `python-dotenv` if you want auto-loading):

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/expense_tracker
```

> Tables are created automatically on first startup via `Base.metadata.create_all()`.

### 6 — Run the server

```bash
# Run from the PARENT folder of expense_tracker/
uvicorn expense_tracker.main:app --reload
```

The API is now live at **http://127.0.0.1:8000**

---

## API Reference

Interactive docs (Swagger UI): **http://127.0.0.1:8000/docs**

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/expenses` | Create a single expense |
| `POST` | `/expenses/bulk` | Create multiple expenses |
| `GET` | `/expenses` | List all expenses (paginated) |
| `GET` | `/expenses/{id}` | Get one expense by ID |
| `PATCH` | `/expenses/{id}` | Partially update an expense |
| `DELETE` | `/expenses/{id}` | Delete an expense |

**Create expense — request body:**
```json
{
  "description": "Walmart",
  "amount": 45.50,
  "date": "2026-03-26"
}
```

**Bulk create — request body:**
```json
[
  { "description": "Walmart",   "amount": 45.50, "date": "2026-03-26" },
  { "description": "Starbucks", "amount": 6.75,  "date": "2026-03-26" }
]
```

**Update expense (PATCH) — all fields optional:**
```json
{ "amount": 99.99 }
```

### Reports

| Method | Endpoint | Query Params | Description |
|--------|----------|--------------|-------------|
| `GET` | `/reports/summary` | — | Spending totals grouped by shop |
| `GET` | `/reports/weekly` | — | Last 7 days total |
| `GET` | `/reports/monthly` | `month`, `year` | Total for a specific month |
| `GET` | `/reports/yearly` | `year` | Total for a specific year |

---

## Running Tests

Tests use an **in-memory SQLite** database — no PostgreSQL required.

```bash
# From the parent folder of expense_tracker/
pytest expense_tracker/tests/ -v
```

Expected output:

```
tests/test_expenses.py::TestCreateExpense::test_creates_successfully         PASSED
tests/test_expenses.py::TestCreateExpense::test_rejects_zero_amount          PASSED
tests/test_expenses.py::TestCreateExpense::test_rejects_negative_amount      PASSED
tests/test_expenses.py::TestCreateExpense::test_rejects_empty_description    PASSED
tests/test_expenses.py::TestCreateExpense::test_rejects_missing_fields       PASSED
tests/test_expenses.py::TestBulkCreate::test_bulk_creates_multiple           PASSED
...
tests/test_reports.py::TestWeeklyReport::test_includes_expense_from_today    PASSED
tests/test_reports.py::TestWeeklyReport::test_excludes_expense_older_than... PASSED
...
```

Run with coverage:
```bash
pip install pytest-cov
pytest expense_tracker/tests/ -v --cov=expense_tracker --cov-report=term-missing
```

---

## Design Decisions

**Separation of concerns** — `crud.py` has zero FastAPI imports. This means DB logic is testable in isolation without spinning up HTTP.

**Pydantic v2 schemas** — All inputs validated before touching the DB. Invalid amounts (≤ 0) and empty descriptions are rejected at the schema layer with a `422` before any DB call.

**Dependency injection for DB sessions** — `get_db` is injected via `Depends()`. In tests, this dependency is overridden with a rolled-back SQLite session, so every test starts clean.

**Rollback-per-test isolation** — Each test opens a transaction that is rolled back at teardown, making tests order-independent and fast.
