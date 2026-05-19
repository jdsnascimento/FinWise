from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..services.report_service import ReportService
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/by-category")
async def report_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Relatório de gastos por categoria"""
    if not start_date:
        start_date = (date.today().replace(day=1)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    return ReportService.get_expense_by_category(
        db, current_user.id,
        date.fromisoformat(start_date),
        date.fromisoformat(end_date)
    )

@router.get("/by-card")
async def report_by_card(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Relatório de gastos por cartão"""
    if not start_date:
        start_date = (date.today().replace(day=1)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    return ReportService.get_expense_by_card(
        db, current_user.id,
        date.fromisoformat(start_date),
        date.fromisoformat(end_date)
    )

@router.get("/monthly-evolution")
async def monthly_evolution(
    months: int = Query(12, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evolução mensal dos últimos meses"""
    return ReportService.get_monthly_evolution(db, current_user.id, months)

@router.get("/payment-methods")
async def payment_methods(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Análise por método de pagamento"""
    if not start_date:
        start_date = (date.today().replace(day=1)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    return ReportService.get_payment_methods_analysis(
        db, current_user.id,
        date.fromisoformat(start_date),
        date.fromisoformat(end_date)
    )

@router.get("/full-report")
async def full_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    report_type: str = "complete",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Relatório completo consolidado"""
    if not start_date:
        # Últimos 30 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = date.fromisoformat(start_date)
    
    if not end_date:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end_date)
    
    return ReportService.get_full_report(
        db, current_user.id, start_date, end_date, report_type
    )