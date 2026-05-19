from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List

from ..models.bill import Bill, BillStatus
from ..models.credit_card import CreditCard
from ..services.whatsapp_service import whatsapp_service
from ..config import settings

class NotificationService:
    
    @staticmethod
    def check_upcoming_bills(db: Session):
        """Verifica contas próximas do vencimento e envia notificações"""
        today = date.today()
        upcoming_dates = [today + timedelta(days=d) for d in range(4)]  # Hoje + 3 dias
        
        upcoming_bills = db.query(Bill).filter(
            Bill.status == BillStatus.PENDING,
            Bill.due_date.in_(upcoming_dates)
        ).all()
        
        notifications = []
        
        for bill in upcoming_bills:
            days_until_due = (bill.due_date - today).days
            
            # Criar notificação
            notification = {
                'user_id': bill.user_id,
                'bill_id': bill.id,
                'description': bill.description,
                'amount': float(bill.total_amount),
                'due_date': bill.due_date.isoformat(),
                'days_until_due': days_until_due,
                'urgency': 'high' if days_until_due <= 1 else 'medium',
                'message': NotificationService._generate_message(bill, days_until_due)
            }
            
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def _generate_message(bill: Bill, days_until_due: int) -> str:
        """Gera mensagem personalizada"""
        if days_until_due == 0:
            return f"🔴 HOJE: {bill.description} - R$ {bill.total_amount:,.2f}"
        elif days_until_due == 1:
            return f"🟡 Amanhã: {bill.description} - R$ {bill.total_amount:,.2f}"
        else:
            return f"📅 Em {days_until_due} dias: {bill.description} - R$ {bill.total_amount:,.2f}"
    
    @staticmethod
    def check_card_limits(db: Session):
        """Verifica limites dos cartões"""
        cards = db.query(CreditCard).filter(
            CreditCard.active == True
        ).all()
        
        alerts = []
        
        for card in cards:
            if card.limit_amount > 0:
                usage_percentage = float((card.limit_amount - card.available_limit) / card.limit_amount * 100)
                
                if usage_percentage >= 90:
                    alerts.append({
                        'user_id': card.user_id,
                        'card_id': card.id,
                        'card_name': card.name,
                        'usage_percentage': round(usage_percentage, 1),
                        'available_limit': float(card.available_limit),
                        'limit': float(card.limit_amount),
                        'level': 'critical'
                    })
                elif usage_percentage >= 75:
                    alerts.append({
                        'user_id': card.user_id,
                        'card_id': card.id,
                        'card_name': card.name,
                        'usage_percentage': round(usage_percentage, 1),
                        'available_limit': float(card.available_limit),
                        'limit': float(card.limit_amount),
                        'level': 'warning'
                    })
        
        return alerts
    
    @staticmethod
    async def send_whatsapp_notification(user_id: int, phone: str, message: str):
        """Envia notificação via WhatsApp"""
        try:
            # Buscar instância do usuário
            from ..models.whatsapp_instance import WhatsAppInstance, ConnectionStatus
            
            # Aqui você implementaria a lógica de envio
            # await whatsapp_service.send_message(instance_name, phone, message)
            pass
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")