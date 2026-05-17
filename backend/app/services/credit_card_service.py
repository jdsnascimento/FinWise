from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from ..models.credit_card import CreditCard
from ..models.bill import Bill, BillStatus
from ..schemas.credit_card import CreditCardCreate, CreditCardUpdate
from fastapi import HTTPException, status

class CreditCardService:
    
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
        
        # Se alterou o limite, recalcular disponível
        if 'limit_amount' in update_data:
            old_limit = card.limit_amount
            new_limit = update_data['limit_amount']
            
            # Calcular total gasto no cartão
            total_spent = db.query(func.sum(Bill.total_amount)).filter(
                Bill.card_id == card.id,
                Bill.status == BillStatus.PENDING
            ).scalar() or Decimal('0')
            
            # Novo disponível = novo limite - gastos pendentes
            update_data['available_limit'] = new_limit - total_spent
            
            if update_data['available_limit'] < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Novo limite é menor que o total de gastos pendentes"
                )
        
        for field, value in update_data.items():
            setattr(card, field, value)
        
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
            Bill.status == BillStatus.PENDING
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
            "next_due_date": CreditCardService._calculate_next_due(card.due_day)
        }
    
    @staticmethod
    def _calculate_next_closing(closing_day: int) -> date:
        """Calcula próxima data de fechamento"""
        today = date.today()
        
        if today.day <= closing_day:
            # Fechamento ainda este mês
            return today.replace(day=closing_day)
        else:
            # Fechamento próximo mês
            if today.month == 12:
                return date(today.year + 1, 1, closing_day)
            else:
                return date(today.year, today.month + 1, closing_day)
    
    @staticmethod
    def _calculate_next_due(due_day: int) -> date:
        """Calcula próximo vencimento"""
        today = date.today()
        closing_day = CreditCardService._calculate_next_closing(15).day  # Aproximado
        
        if today.day <= due_day:
            return today.replace(day=due_day)
        else:
            if today.month == 12:
                return date(today.year + 1, 1, due_day)
            else:
                return date(today.year, today.month + 1, due_day)