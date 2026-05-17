from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models.user import User
from ..schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomeResponse,
    IncomeSummary,
    IncomeStatusEnum
)
from ..services.income_service import IncomeService
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/api/incomes", tags=["incomes"])

@router.post("/", response_model=IncomeResponse, status_code=201)
async def create_income(
    income_data: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria nova receita"""
    return IncomeService.create_income(db, current_user.id, income_data)

@router.get("/", response_model=List[IncomeResponse])
async def list_incomes(
    status: Optional[IncomeStatusEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista receitas com filtros"""
    return IncomeService.get_user_incomes(
        db, current_user.id, status, start_date, end_date, category_id, search
    )

@router.get("/summary", response_model=IncomeSummary)
async def get_incomes_summary(
    month: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resumo de receitas"""
    return IncomeService.get_incomes_summary(db, current_user.id, month)

@router.get("/{income_id}", response_model=IncomeResponse)
async def get_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém receita específica"""
    return IncomeService.get_income_by_id(db, income_id, current_user.id)

@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: int,
    income_data: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza receita"""
    return IncomeService.update_income(db, income_id, current_user.id, income_data)

@router.patch("/{income_id}/receive")
async def receive_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca receita como recebida"""
    from ..schemas.income import IncomeUpdate
    return IncomeService.update_income(
        db, income_id, current_user.id,
        IncomeUpdate(status=IncomeStatusEnum.RECEIVED)
    )

@router.delete("/{income_id}")
async def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exclui receita"""
    return IncomeService.delete_income(db, income_id, current_user.id)