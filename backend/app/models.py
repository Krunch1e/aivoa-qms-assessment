"""
Pydantic models — this is the SOURCE OF TRUTH for the Complaint shape.
If you add/change a field, update this file first, then propagate to
db_models.py and frontend/src/store/complaintSlice.js.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class RiskAssessment(BaseModel):
    severity: Optional[Literal["Minor", "Major", "Critical"]] = None
    suggested_next_action: Optional[str] = None
    initial_risk_assessment: Optional[str] = None


class Complaint(BaseModel):
    """Full complaint object. All fields optional since it gets built up
    incrementally across multiple chat turns."""

    complaint_source: Optional[str] = None          # Pharmacy | Email | Phone | ...
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_lot_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    originating_site_block: Optional[str] = None
    impacted_npm: Optional[str] = None                # Non-Product Materials
    complaint_category: Optional[str] = None
    complaint_description: Optional[str] = None
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)

    @property
    def is_ready_to_commit(self) -> bool:
        """Mirrors the 'Ready to Commit' badge logic in the UI.
        Tune this list to whichever fields you consider mandatory."""
        required = [
            self.product_name,
            self.batch_lot_number,
            self.complaint_description,
            self.risk_assessment.severity,
        ]
        return all(required)


class ChatRequest(BaseModel):
    message: str
    # current form state, sent by the frontend so edit_complaint has context
    current_complaint: Optional[Complaint] = None


class ChatResponse(BaseModel):
    reply: str                 # short natural-language confirmation for the chat log
    complaint: Complaint        # full updated complaint object
    tool_used: Literal["log_complaint", "edit_complaint", "extract_document"]
