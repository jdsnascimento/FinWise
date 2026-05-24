from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models.user import User
from ..schemas.bill import (
    BillCreate, 
    BillUpdate, 
    BillResponse, 
    BillFilter, 
    BillSummary,
    BillStatusEnum,
    PaymentTypeEnum
)
from ..services.bill_service import BillService
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/api/bills", tags=["bills"])

@router.post("/", response_model=BillResponse, status_code=201)
async def create_bill(
    bill_data: BillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova conta a pagar"""
    return BillService.create_bill(db, current_user.id, bill_data)

@router.get("/", response_model=List[BillResponse])
async def list_bills(
    status: Optional[BillStatusEnum] = None,
    category_id: Optional[int] = None,
    card_id: Optional[int] = None,
    payment_type: Optional[PaymentTypeEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    billing_month: Optional[date] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    
    db: Session = Depends(get_db)
):
    """Lista contas com filtros"""
    filters = BillFilter(
        status=status,
        category_id=category_id,
        card_id=card_id,
        payment_type=payment_type,
        start_date=start_date,
        end_date=end_date,
        billing_month=billing_month,
        search=search
    )
    return BillService.get_user_bills(db, current_user.id, filters)

@router.get("/summary", response_model=BillSummary)
async def get_bills_summary(
    billing_month: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna resumo financeiro"""
    return BillService.get_bills_summary(db, current_user.id, billing_month)

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de uma conta"""
    return BillService.get_bill_by_id(db, bill_id, current_user.id)

@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: int,
    bill_data: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza uma conta"""
    return BillService.update_bill(db, bill_id, current_user.id, bill_data)

@router.patch("/{bill_id}/pay")
async def pay_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca conta como paga"""
    from ..schemas.bill import BillUpdate
    return BillService.update_bill(
        db, bill_id, current_user.id, 
        BillUpdate(status=BillStatusEnum.PAID)
    )

@router.patch("/{bill_id}/cancel")
async def cancel_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancela uma conta"""
    from ..schemas.bill import BillUpdate
    return BillService.update_bill(
        db, bill_id, current_user.id,
        BillUpdate(status=BillStatusEnum.CANCELLED)
    )

@router.delete("/{bill_id}")
async def delete_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exclui uma conta pendente"""
    return BillService.delete_bill(db, bill_id, current_user.id)

    