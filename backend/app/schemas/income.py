from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class IncomeStatusEnum(str, Enum):
    PENDING = "pending"
    RECEIVED = "received"
    LATE = "late"
    CANCELLED = "cancelled"

class RecurrenceTypeEnum(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class IncomeBase(BaseModel):
    description: str = Field(..., min_length=3, max_length=255)
    amount: Decimal = Field(..., gt=0)
    expected_date: date
    category_id: int
    recurring: bool = False
    recurrence_type: Optional[RecurrenceTypeEnum] = None
    notes: Optional[str] = None

class IncomeCreate(IncomeBase):
    pass

class IncomeUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=3, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    expected_date: Optional[date] = None
    received_date: Optional[date] = None
    category_id: Optional[int] = None
    status: Optional[IncomeStatusEnum] = None
    recurring: Optional[bool] = None
    recurrence_type: Optional[RecurrenceTypeEnum] = None
    notes: Optional[str] = None

class IncomeResponse(IncomeBase):
    id: int
    received_date: Optional[date] = None
    status: IncomeStatusEnum
    source: str
    created_at: datetime
    updated_at: Optional[datetime]
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    
    class Config:
        from_attributes = True

class IncomeSummary(BaseModel):
    """Resumo de receitas"""
    total_expected: Decimal = Decimal('0')
    total_received: Decimal = Decimal('0')
    total_pending: Decimal = Decimal('0')
    pending_count: int = 0
    next_expected: Optional[date] = None
    next_amount: Decimal = Decimal('0')