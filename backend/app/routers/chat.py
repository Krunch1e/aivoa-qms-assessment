import json
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from typing import Optional

from ..models import Complaint, ChatResponse
from ..agent.graph import agent_app
from ..db import get_db
from ..db_models import ComplaintRecord

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(""),
    current_complaint: Optional[str] = Form(None),  # JSON string from frontend
    file: Optional[UploadFile] = File(None),
):
    """
    Single endpoint for all 3 tools. The frontend always POSTs here as
    multipart/form-data (so file upload and plain chat share one code path).

    - `message`: the chat input text
    - `current_complaint`: JSON string of the current form state (None if
      this is the first message / new complaint)
    - `file`: optional uploaded PDF
    """
    parsed_current = Complaint(**json.loads(current_complaint)) if current_complaint else None
    file_bytes = await file.read() if file else None
    filename = file.filename if file else None

    initial_state = {
        "user_message": message,
        "current_complaint": parsed_current,
        "file_bytes": file_bytes,
        "filename": filename,
    }

    final_state = agent_app.invoke(initial_state)

    return ChatResponse(
        reply=final_state["reply"],
        complaint=final_state["result_complaint"],
        tool_used=final_state["tool_used"],
    )


@router.post("/commit")
def commit_complaint(complaint: Complaint, db: Session = Depends(get_db)):
    """Persist the finalized complaint to the QMS database."""
    # Extract risk assessment nested dictionary explicitly
    risk = complaint.risk_assessment
    
    db_record = ComplaintRecord(
        complaint_source=complaint.complaint_source,
        customer_name=complaint.customer_name,
        product_name=complaint.product_name,
        product_strength=complaint.product_strength,
        batch_lot_number=complaint.batch_lot_number,
        affected_quantity=complaint.affected_quantity,
        manufacturing_date=complaint.manufacturing_date,
        expiry_date=complaint.expiry_date,
        originating_site_block=complaint.originating_site_block,
        impacted_npm=complaint.impacted_npm,
        complaint_category=complaint.complaint_category,
        complaint_description=complaint.complaint_description,
        severity=risk.severity if risk else None,
        suggested_next_action=risk.suggested_next_action if risk else None,
        initial_risk_assessment=risk.initial_risk_assessment if risk else None,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return {"status": "success", "id": db_record.id}
