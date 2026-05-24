from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class BillStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentTypeEnum(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BOLETO = "boleto"
    TRANSFER = "transfer"

class BillSourceEnum(str, Enum):
    MANUAL = "manual"
    WHATSAPP = "whatsapp"
    IMPORT = "import"

# Schema base
class BillBase(BaseModel):
    description: str = Field(..., min_length=3, max_length=255)
    amount: Decimal = Field(..., gt=0)
    total_amount: Optional[Decimal] = None
    installments: int = Field(default=1, ge=1, le=48)
    current_installment: int = Field(default=1, ge=1)
    purchase_date: date
    due_date: Optional[date] = None
    category_id: int
    card_id: Optional[int] = None
    payment_type: PaymentTypeEnum
    notes: Optional[str] = None

class BillCreate(BillBase):
    pass

    @validator('total_amount', always=True)
    def set_total_amount(cls, v, values):
        """Define o total_amount igual ao amount (pois o amount agora representa o valor total da compra)"""
        if v is None:
            return values.get('amount', 0)
        return v

class BillUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=3, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    total_amount: Optional[Decimal] = None
    category_id: Optional[int] = None
    card_id: Optional[int] = None
    due_date: Optional[date] = None
    status: Optional[BillStatusEnum] = None
    notes: Optional[str] = None

class BillInstallmentResponse(BaseModel):
    id: int
    installment_number: int
    amount: Decimal
    due_date: date
    billing_month: date
    status: BillStatusEnum
    paid_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BillResponse(BillBase):
    id: int
    total_amount: Decimal
    billing_month: date
    status: BillStatusEnum
    source: BillSourceEnum
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    installments_list: Optional[List[BillInstallmentResponse]] = []
    
    # Campos relacionados
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    card_name: Optional[str] = None
    
    class Config:
        from_attributes = True

    @property
    def installment_label(self):
        return f"{self.current_installment}/{self.installments}"

class BillFilter(BaseModel):
    """Filtros para listagem de contas"""
    status: Optional[BillStatusEnum] = None
    category_id: Optional[int] = None
    card_id: Optional[int] = None
    payment_type: Optional[PaymentTypeEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    billing_month: Optional[date] = None
    search: Optional[str] = None

class BillSummary(BaseModel):
    """Resumo financeiro para dashboard"""
    total_pending: Decimal = Decimal('0')
    total_paid: Decimal = Decimal('0')
    total_overdue: Decimal = Decimal('0')
    pending_count: int = 0
    next_due: Optional[date] = None
    next_due_amount: Decimal = Decimal('0')