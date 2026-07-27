"""
The 3 mandatory tools. Each returns a (reply_text, Complaint) tuple.
Kept as plain Python functions — LangGraph nodes in graph.py just call these.
"""

import pdfplumber
import io

from ..models import Complaint
from .llm import call_llm_json
from .prompts import (
    LOG_COMPLAINT_SYSTEM_PROMPT,
    EDIT_COMPLAINT_SYSTEM_PROMPT,
    EXTRACT_DOCUMENT_SYSTEM_PROMPT,
    build_edit_user_prompt,
)


def log_complaint(user_message: str) -> tuple[str, Complaint]:
    """Create a new complaint from a natural language prompt."""
    result = call_llm_json(LOG_COMPLAINT_SYSTEM_PROMPT, user_message)
    complaint = Complaint(**result)
    reply = (
        "Complaint parsed successfully. I've extracted the product details, "
        "mapped the batch information, and generated an initial risk "
        "assessment."
    )
    return reply, complaint


def edit_complaint(user_message: str, current_complaint: Complaint) -> tuple[str, Complaint]:
    """Update an existing complaint via natural language correction."""
    current_json = current_complaint.model_dump_json()
    user_prompt = build_edit_user_prompt(current_json, user_message)
    result = call_llm_json(EDIT_COMPLAINT_SYSTEM_PROMPT, user_prompt)
    updated = Complaint(**result)
    reply = "Got it — I've updated the complaint with the new information."
    return reply, updated


def extract_document(file_bytes: bytes, filename: str) -> tuple[str, Complaint]:
    """Extract complaint details from an uploaded PDF."""
    text = _extract_pdf_text(file_bytes) if filename.lower().endswith(".pdf") else file_bytes.decode(
        "utf-8", errors="ignore"
    )
    result = call_llm_json(EXTRACT_DOCUMENT_SYSTEM_PROMPT, text)
    complaint = Complaint(**result)
    reply = (
        f"PDF analysis complete. I've successfully extracted the complaint "
        f"details from {filename} and populated the form."
    )
    return reply, complaint


def _extract_pdf_text(file_bytes: bytes) -> str:
    text_chunks = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)
