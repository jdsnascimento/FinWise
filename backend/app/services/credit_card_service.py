import calendar
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta
from ..models.credit_card import CreditCard
from ..models.bill import Bill, BillStatus, PaymentType
from ..schemas.credit_card import CreditCardCreate, CreditCardUpdate
from fastapi import HTTPException, status

class CreditCardService:
    
    @staticmethod
    def recalculate_available_limit(db: Session, card_id: int):
        """Recalcula o limite disponível de um cartão com base nas despesas pendentes/vencidas"""
        card = db.query(CreditCard).filter(CreditCard.id == card_id).first()
        if not card:
            return None
        
        # Somar as despesas pendentes/vencidas no cartão
        total_spent = db.query(func.sum(Bill.amount)).filter(
            Bill.card_id == card.id,
            Bill.status.in_([BillStatus.PENDING, BillStatus.OVERDUE]),
            Bill.payment_type == PaymentType.CREDIT_CARD
        ).scalar() or Decimal('0')
        
        card.available_limit = card.limit_amount - total_spent
        db.flush()
        return card

    @staticmethod
    def get_user_cards(db: Session, user_id: int, active_only: bool = False):
        """Lista todos os cartões do usuário"""
        query = db.query(CreditCard).filter(CreditCard.user_id == user_id)
        if active_only:
            query = query.filter(CreditCard.active == True)
        return query.order_by(CreditCard.name).all()
    
    @staticmethod
    def get_card_by_id(db: Session, card_id: int, user_id: int):
        """Busca cartão específico do usuário"""
        card = db.query(CreditCard).filter(
            CreditCard.id == card_id,
            CreditCard.user_id == user_id
        ).first()
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cartão não encontrado"
            )
        return card
    
    @staticmethod
    def create_card(db: Session, user_id: int, card_data: CreditCardCreate):
        """Cria novo cartão"""
        # Verificar limite de cartões (opcional)
        card_count = db.query(CreditCard).filter(
            CreditCard.user_id == user_id,
            CreditCard.active == True
        ).count()
        
        if card_count >= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limite máximo de 10 cartões ativos"
            )
        
        card = CreditCard(
            user_id=user_id,
            name=card_data.name,
            bank=card_data.bank,
            flag=card_data.flag,
            limit_amount=card_data.limit_amount,
            available_limit=card_data.limit_amount,  # Inicia com limite total
            closing_day=card_data.closing_day,
            due_day=card_data.due_day,
            color=card_data.color
        )
        
        db.add(card)
        db.commit()
        db.refresh(card)
        
        return card
    
    @staticmethod
    def update_card(db: Session, card_id: int, user_id: int, card_data: CreditCardUpdate):
        """Atualiza cartão existente"""
        card = CreditCardService.get_card_by_id(db, card_id, user_id)
        
        # Atualizar campos
        update_data = card_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(card, field, value)
            
        # Recalcular limite disponível com base nos dados atualizados
        CreditCardService.recalculate_available_limit(db, card.id)
        
        if card.available_limit < 0:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Novo limite é menor que o total de gastos pendentes"
            )
        
        db.commit()
        db.refresh(card)
        
        return card
    
    @staticmethod
    def delete_card(db: Session, card_id: int, user_id: int):
        """Desativa cartão (soft delete)"""
        card = CreditCardService.get_card_by_id(db, card_id, user_id)
        
        # Verificar se há contas pendentes
        pending_bills = db.query(Bill).filter(
            Bill.card_id == card.id,
            Bill.status.in_([BillStatus.PENDING, BillStatus.OVERDUE])
        ).count()
        
        if pending_bills > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível desativar cartão com {pending_bills} contas pendentes"
            )
        
        card.active = False
        db.commit()
        
        return {"message": "Cartão desativado com sucesso"}
    
    @staticmethod
    def get_card_summary(db: Session, card_id: int, user_id: int):
        """Retorna resumo do cartão com gastos do mês"""
        card = CreditCardService.get_card_by_id(db, card_id, user_id)
        
        # Gastos do mês atual
        current_month = date.today().replace(day=1)
        monthly_spent = db.query(func.sum(Bill.total_amount)).filter(
            Bill.card_id == card.id,
            Bill.billing_month == current_month,
            Bill.status == BillStatus.PENDING
        ).scalar() or Decimal('0')
        
        # Calcular porcentagem de uso
        usage_percentage = 0
        if card.limit_amount > 0:
            usage_percentage = float((card.limit_amount - card.available_limit) / card.limit_amount * 100)
        
        return {
            "card": card,
            "current_bill_total": monthly_spent,
            "usage_percentage": round(usage_percentage, 1),
            "next_closing_date": CreditCardService._calculate_next_closing(card.closing_day),
            "next_due_date": CreditCardService._calculate_next_due(card.due_day, card.closing_day)
        }
    
    @staticmethod
    def _day_in_month(year: int, month: int, day: int) -> int:
        """Retorna o dia efetivo no mês (ex.: 31 em fevereiro vira 28/29)."""
        return min(day, calendar.monthrange(year, month)[1])
    
    @staticmethod
    def _calculate_next_closing(closing_day: int) -> date:
        """Calcula próxima data de fechamento"""
        today = date.today()
        actual_closing = CreditCardService._day_in_month(
            today.year, today.month, closing_day
        )
        
        if today.day <= actual_closing:
            return today.replace(day=actual_closing)
        
        next_month = today.replace(day=1) + relativedelta(months=1)
        return next_month.replace(
            day=CreditCardService._day_in_month(
                next_month.year, next_month.month, closing_day
            )
        )
    
    @staticmethod
    def _calculate_next_due(due_day: int, closing_day: int) -> date:
        """Calcula próximo vencimento após o próximo fechamento da fatura."""
        next_closing = CreditCardService._calculate_next_closing(closing_day)
        due_month = next_closing.replace(day=1) + relativedelta(months=1)
        return due_month.replace(
            day=CreditCardService._day_in_month(due_month.year, due_month.month, due_day)
        )