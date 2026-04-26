from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    uploaded_by = Column(BigInteger, ForeignKey("users.id"))
    image_url = Column(Text, nullable=False)
    raw_ocr_text = Column(Text)
    parsed_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="receipts")
    uploader = relationship("User", back_populates="uploaded_receipts")
    expenses = relationship("Expense", back_populates="receipt")
