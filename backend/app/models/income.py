from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class IncomeStatus(str, enum.Enum):
    PENDING = "pending"
    RECEIVED = "received"
    LATE = "late"
    CANCELLED = "cancelled"

class RecurrenceType(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Income(Base):
    __tablename__ = "incomes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    expected_date = Column(Date, nullable=False, comment="Data prevista para receber")
    received_date = Column(Date, nullable=True, comment="Data que foi realmente recebido")
    
    status = Column(Enum(IncomeStatus), default=IncomeStatus.PENDING)
    recurring = Column(Boolean, default=False)
    recurrence_type = Column(Enum(RecurrenceType), nullable=True)
    
    source = Column(String(20), default="manual")
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="incomes")
    category = relationship("Category")
    
    def __repr__(self):
        return f"<Income(id={self.id}, description='{self.description}', amount={self.amount})>"