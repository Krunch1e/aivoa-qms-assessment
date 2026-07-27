from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .db import Base


class ComplaintRecord(Base):
    """SQLAlchemy mirror of the Pydantic Complaint model.
    Keep field names identical to models.py to avoid mapping bugs."""

    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_source = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    product_strength = Column(String, nullable=True)
    batch_lot_number = Column(String, nullable=True)
    affected_quantity = Column(String, nullable=True)
    manufacturing_date = Column(String, nullable=True)
    expiry_date = Column(String, nullable=True)
    originating_site_block = Column(String, nullable=True)
    impacted_npm = Column(String, nullable=True)
    complaint_category = Column(String, nullable=True)
    complaint_description = Column(Text, nullable=True)

    severity = Column(String, nullable=True)
    suggested_next_action = Column(Text, nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
