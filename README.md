# AIVOA — AI-Powered Customer Complaint Management System

Built for the AIVOA.AI "AI Product Engineer (Fresher)" technical assessment.

See `AGENTS.md` for the architecture rules and conventions this codebase
follows — read it before extending anything.

## Stack

- **Frontend:** React + Redux Toolkit (Vite)
- **Backend:** FastAPI
- **Agent orchestration:** LangGraph
- **LLM:** Groq (`gemma2-9b-it`, fallback `llama-3.3-70b-versatile`)
- **DB:** PostgreSQL (SQLAlchemy)
- **Font:** Google Inter

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env      # fill in GROQ_API_KEY and DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

Make sure Postgres is running and the database in `DATABASE_URL` exists
(`createdb aivoa` or equivalent).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The frontend expects the backend at
`http://localhost:8000` (override with a `VITE_API_BASE` env var if needed).

## How it works

1. Type a natural language complaint into the AIVOA Copilot chat (right
   panel) — e.g. *"Apollo Pharmacy reported discolored capsules in
   Amoxicillin capsules 500mg."*
2. The backend routes this to the `log_complaint` tool, which calls the
   Groq LLM to extract structured fields AND perform an initial risk
   assessment (severity, suggested next action, reasoning).
3. The response populates the Log Customer Complaint form (left panel) via
   Redux — the form is never edited by hand.
4. Send a follow-up correction (e.g. *"Sorry, batch number is BMX24602 and
   affected quantity is 48 capsules"*) — this routes to `edit_complaint`,
   which updates only the mentioned fields, preserves the rest, and
   re-evaluates the risk assessment.
5. Upload a PDF instead of typing — this routes to `extract_document`,
   which extracts text from the PDF and runs the same extraction/reasoning
   pipeline. You can still send follow-up corrections after extraction.

## Routing logic

Kept intentionally simple (see `backend/app/agent/graph.py`):

```
file attached?        → extract_document
no complaint yet?      → log_complaint
otherwise              → edit_complaint
```

## What I'd improve with more time

- Persist the conversation + complaint history to Postgres on every turn
  (currently the DB models exist but aren't wired into the chat endpoint —
  wire `db_models.ComplaintRecord` into `routers/chat.py` to save each
  commit).
- Add the bonus features (duplicate detection, CAPA recommendation, etc.)
  once the core 3-tool flow is proven reliable across more complaint types.
- Streaming responses in the chat instead of waiting for the full LLM
  response.
- Proper auth / multi-user support (out of scope for this assessment).

## Sample data

See `sample-data/` for example complaint PDFs used to test the
`extract_document` tool.
