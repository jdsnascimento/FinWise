from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import date

from ..models.income import Income, IncomeStatus
from ..models.category import Category
from ..schemas.income import IncomeCreate, IncomeUpdate
from fastapi import HTTPException, status

class IncomeService:
    
    @staticmethod
    def create_income(db: Session, user_id: int, income_data: IncomeCreate):
        """Cria nova receita"""
        # Validar categoria
        category = db.query(Category).filter(
            Category.id == income_data.category_id,
            Category.user_id == user_id,
            Category.type == 'income'
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria inválida. Use uma categoria do tipo 'receita'"
            )
        
        # Validar recorrência
        if income_data.recurring and not income_data.recurrence_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de recorrência é obrigatório para receitas recorrentes"
            )
        
        income = Income(
            user_id=user_id,
            category_id=income_data.category_id,
            description=income_data.description,
            amount=income_data.amount,
            expected_date=income_data.expected_date,
            status=IncomeStatus.PENDING,
            recurring=income_data.recurring,
            recurrence_type=income_data.recurrence_type,
            notes=income_data.notes,
            source='manual'
        )
        
        db.add(income)
        db.commit()
        db.refresh(income)
        
        return income
    
    @staticmethod
    def get_user_incomes(db: Session, user_id: int, 
                         status: IncomeStatus = None,
                         start_date: date = None,
                         end_date: date = None,
                         category_id: int = None,
                         search: str = None):
        """Lista receitas com filtros"""
        query = db.query(Income).filter(Income.user_id == user_id)
        
        if status:
            query = query.filter(Income.status == status)
        if start_date:
            query = query.filter(Income.expected_date >= start_date)
        if end_date:
            query = query.filter(Income.expected_date <= end_date)
        if category_id:
            query = query.filter(Income.category_id == category_id)
        if search:
            query = query.filter(Income.description.ilike(f"%{search}%"))
        
        incomes = query.order_by(Income.expected_date.asc()).all()
        
        # Adicionar info da categoria
        for income in incomes:
            if income.category:
                income.category_name = income.category.name
                income.category_color = income.category.color
        
        return incomes
    
    @staticmethod
    def get_income_by_id(db: Session, income_id: int, user_id: int):
        """Busca receita específica"""
        income = db.query(Income).filter(
            Income.id == income_id,
            Income.user_id == user_id
        ).first()
        
        if not income:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receita não encontrada"
            )
        
        if income.category:
            income.category_name = income.category.name
            income.category_color = income.category.color
        
        return income
    
    @staticmethod
    def update_income(db: Session, income_id: int, user_id: int, income_data: IncomeUpdate):
        """Atualiza receita"""
        income = IncomeService.get_income_by_id(db, income_id, user_id)
        
        # Se marcar como recebido
        if income_data.status == IncomeStatus.RECEIVED and income.status != IncomeStatus.RECEIVED:
            income.status = IncomeStatus.RECEIVED
            income.received_date = income_data.received_date or date.today()
        
        # Atualizar outros campos
        update_data = income_data.dict(exclude_unset=True, exclude={'status', 'received_date'})
        
        for field, value in update_data.items():
            if value is not None:
                setattr(income, field, value)
        
        db.commit()
        db.refresh(income)
        
        return income
    
    @staticmethod
    def delete_income(db: Session, income_id: int, user_id: int):
        """Remove receita"""
        income = IncomeService.get_income_by_id(db, income_id, user_id)
        db.delete(income)
        db.commit()
        return {"message": "Receita excluída com sucesso"}
    
    @staticmethod
    def get_incomes_summary(db: Session, user_id: int, month: date = None):
        """Resumo de receitas do mês"""
        if not month:
            month = date.today().replace(day=1)
        
        # Próxima receita esperada
        next_income = db.query(Income).filter(
            Income.user_id == user_id,
            Income.status == IncomeStatus.PENDING,
            Income.expected_date >= date.today()
        ).order_by(Income.expected_date.asc()).first()
        
        # Totais do mês
        month_end = month.replace(day=28)  # Aproximado
        
        totals = db.query(
            func.sum(Income.amount).label('total'),
            Income.status
        ).filter(
            Income.user_id == user_id,
            Income.expected_date >= month,
            Income.expected_date <= month_end
        ).group_by(Income.status).all()
        
        summary = {
            'total_expected': Decimal('0'),
            'total_received': Decimal('0'),
            'total_pending': Decimal('0'),
            'pending_count': 0,
            'next_expected': next_income.expected_date if next_income else None,
            'next_amount': next_income.amount if next_income else Decimal('0')
        }
        
        for total in totals:
            if total.status == IncomeStatus.PENDING:
                summary['total_pending'] = total.total or Decimal('0')
            elif total.status == IncomeStatus.RECEIVED:
                summary['total_received'] = total.total or Decimal('0')
            summary['total_expected'] += (total.total or Decimal('0'))
        
        summary['pending_count'] = db.query(Income).filter(
            Income.user_id == user_id,
            Income.status == IncomeStatus.PENDING
        ).count()
        
        return summary