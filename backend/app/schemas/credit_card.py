from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CreditCardBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    bank: str = Field(..., min_length=2, max_length=50)
    flag: str = Field(..., min_length=2, max_length=30)
    limit_amount: Decimal = Field(..., gt=0)
    closing_day: int = Field(..., ge=1, le=31)
    due_day: int = Field(..., ge=1, le=31)
    color: str = Field(default="#6366f1", max_length=7)

class CreditCardCreate(CreditCardBase):
    pass

class CreditCardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    bank: Optional[str] = Field(None, min_length=2, max_length=50)
    flag: Optional[str] = Field(None, min_length=2, max_length=30)
    limit_amount: Optional[Decimal] = Field(None, gt=0)
    closing_day: Optional[int] = Field(None, ge=1, le=31)
    due_day: Optional[int] = Field(None, ge=1, le=31)
    color: Optional[str] = Field(None, max_length=7)
    active: Optional[bool] = None

class CreditCardResponse(CreditCardBase):
    id: int
    available_limit: Decimal
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CreditCardSummary(BaseModel):
    """Resumo do cartão para dashboard"""
    id: int
    name: str
    bank: str
    flag: str
    limit_amount: Decimal
    available_limit: Decimal
    usage_percentage: float
    color: str
    current_bill_total: Decimal = Decimal('0')
    
    class Config:
        from_attributes = True