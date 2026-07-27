# AGENTS.md — Working Agreement for AI Coding Agents in This Repo

This file tells Antigravity (or any other AI coding assistant) how this project
is structured and how to extend it consistently. Read this before generating
or modifying any code in this repo.

## Project Purpose

An AI-Powered Customer Complaint Management System for a pharmaceutical
manufacturing QMS. The frontend form is **never filled manually** — it is
populated and updated exclusively through the AIVOA Copilot chat, which is
backed by a LangGraph agent with three tools:

1. `log_complaint` — create a new complaint from a natural language prompt
2. `edit_complaint` — update fields on the current complaint via natural language
3. `extract_document` — parse an uploaded PDF/email and populate the complaint

## Non-negotiable rules

- **The single source of truth for a complaint's shape is `backend/app/models.py`
  (`Complaint` Pydantic model).** If you need a new field, add it there first,
  then propagate to `db_models.py` (SQLAlchemy) and the frontend Redux slice
  (`frontend/src/store/complaintSlice.js`). Never let these three drift out of sync.
- **Every tool must return a full, valid `Complaint` JSON object** (not a diff,
  not prose) — the merge/diff logic for `edit_complaint` happens in Python
  (`agent/tools.py`), not by asking the LLM to "only return changed fields."
  Have the LLM return the full updated object; it's more reliable than partial
  patches and avoids the frontend needing complex merge logic.
- **Risk assessment is re-run on every `log_complaint` AND `edit_complaint`
  call** — new information can change severity, so never treat the risk
  assessment as write-once.
- **Do not hardcode logic to the example complaints from the assignment doc**
  (Amoxicillin/Apollo Pharmacy, Metformin/Zenith Life Sciences). The extraction
  prompts must generalize to arbitrary pharma complaints — test with at least
  2 different products before considering a tool "done."
- **No production-grade OCR required.** Plain text extraction from PDFs via
  `pdfplumber` is sufficient — don't over-engineer this.
- **Understand generated code before committing.** Per the assignment's own
  instructions, do not paste LLM-generated code you can't explain — you may be
  asked to modify it live in an interview.

## Directory structure

```
backend/
  app/
    main.py              # FastAPI app entrypoint, CORS, router mounting
    models.py            # Pydantic schemas — THE schema source of truth
    db.py                 # SQLAlchemy engine/session
    db_models.py          # SQLAlchemy ORM models
    agent/
      llm.py              # Groq client wrapper (gemma2-9b-it primary)
      prompts.py          # All prompt templates live here, not inline in tools.py
      tools.py             # log_complaint, edit_complaint, extract_document
      graph.py             # LangGraph StateGraph + routing logic
    routers/
      chat.py              # POST /chat endpoint (text + optional file upload)
frontend/
  src/
    store/
      store.js             # Redux store config
      complaintSlice.js     # Complaint state shape — MUST mirror models.py
    api/
      chatApi.js            # fetch wrapper for /chat
    components/
      ComplaintForm.jsx      # Left panel — renders from Redux state, read-only inputs
      CopilotChat.jsx         # Right panel — chat log + input + file upload
    App.jsx
```

## Routing logic (agent/graph.py)

Keep the router dead simple — it does not need to be a clever LLM classifier:

```
if a file is attached           → extract_document
elif no complaint exists yet     → log_complaint
else                              → edit_complaint
```

This is easier to demo, explain in the interview, and debug than an
LLM-based intent classifier, and satisfies the assignment's actual
requirement (the tools exist and work correctly) without adding
unnecessary failure points.

## What NOT to build (explicitly optional per assignment doc)

Do not spend time on these unless the three core tools are fully working
end-to-end first: Complaint Completeness Checker, Root Cause Recommendation,
Duplicate Complaint Detection, CAPA Recommendation, Complaint Summary,
AI Risk Classification beyond the basic severity already required.

## When adding a new field or tool

1. Update `models.py` first.
2. Update `db_models.py` to match.
3. Update the relevant prompt in `prompts.py` so the LLM knows the field exists.
4. Update `complaintSlice.js` on the frontend.
5. Test with a fresh complaint AND an edit to confirm merge logic still works.
