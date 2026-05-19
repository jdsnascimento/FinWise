from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..services.notification_service import NotificationService
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("/upcoming-bills")
async def get_upcoming_bills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica contas próximas do vencimento"""
    notifications = NotificationService.check_upcoming_bills(db)
    # Filtrar apenas do usuário atual
    return [n for n in notifications if n['user_id'] == current_user.id]

@router.get("/card-alerts")
async def get_card_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica alertas de limite dos cartões"""
    alerts = NotificationService.check_card_limits(db)
    return [a for a in alerts if a['user_id'] == current_user.id]