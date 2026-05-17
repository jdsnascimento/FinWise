from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..services.dashboard_service import DashboardService
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary")
async def get_dashboard_summary(
    billing_month: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna resumo completo do dashboard
    
    Parâmetros:
    - billing_month: mês no formato YYYY-MM (opcional, padrão: mês atual)
    """
    month = None
    if billing_month:
        try:
            year, month_num = billing_month.split('-')
            month = date(int(year), int(month_num), 1)
        except:
            pass
    
    return DashboardService.get_financial_summary(db, current_user.id, month)