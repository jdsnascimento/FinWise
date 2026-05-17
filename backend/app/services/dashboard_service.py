from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from ..models.bill import Bill, BillStatus, PaymentType
from ..models.income import Income, IncomeStatus
from ..models.credit_card import CreditCard
from ..models.category import Category

class DashboardService:
    
    @staticmethod
    def get_financial_summary(db: Session, user_id: int, billing_month: date = None):
        """Resumo financeiro completo para dashboard"""
        if not billing_month:
            billing_month = date.today().replace(day=1)
        
        # Receitas do mês
        month_end = billing_month.replace(day=calendar.monthrange(billing_month.year, billing_month.month)[1])
        
        total_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.status == IncomeStatus.RECEIVED,
            Income.received_date >= billing_month,
            Income.received_date <= month_end
        ).scalar() or Decimal('0')
        
        # Despesas do mês
        total_expenses = db.query(func.sum(Bill.total_amount)).filter(
            Bill.user_id == user_id,
            Bill.status.in_([BillStatus.PENDING, BillStatus.PAID]),
            Bill.billing_month == billing_month
        ).scalar() or Decimal('0')
        
        # Despesas pagas
        paid_expenses = db.query(func.sum(Bill.total_amount)).filter(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PAID,
            Bill.billing_month == billing_month
        ).scalar() or Decimal('0')
        
        # Despesas pendentes
        pending_expenses = db.query(func.sum(Bill.total_amount)).filter(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING,
            Bill.billing_month == billing_month
        ).scalar() or Decimal('0')
        
        # Próximos vencimentos
        upcoming_bills = db.query(Bill).filter(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING,
            Bill.due_date >= date.today()
        ).order_by(Bill.due_date.asc()).limit(5).all()
        
        # Cartões de crédito
        cards = db.query(CreditCard).filter(
            CreditCard.user_id == user_id,
            CreditCard.active == True
        ).all()
        
        total_credit_limit = sum(card.limit_amount for card in cards)
        total_used_limit = sum(card.limit_amount - card.available_limit for card in cards)
        
        # Categorias com mais gastos no mês
        top_categories = db.query(
            Category.name,
            Category.color,
            func.sum(Bill.total_amount).label('total')
        ).join(Bill).filter(
            Bill.user_id == user_id,
            Bill.billing_month == billing_month,
            Bill.status.in_([BillStatus.PENDING, BillStatus.PAID])
        ).group_by(Category.id).order_by(func.sum(Bill.total_amount).desc()).limit(5).all()
        
        # Comparativo dos últimos 6 meses
        monthly_comparison = []
        for i in range(5, -1, -1):
            month = billing_month - relativedelta(months=i)
            month_end = month.replace(day=calendar.monthrange(month.year, month.month)[1])
            
            month_income = db.query(func.sum(Income.amount)).filter(
                Income.user_id == user_id,
                Income.status == IncomeStatus.RECEIVED,
                Income.received_date >= month,
                Income.received_date <= month_end
            ).scalar() or Decimal('0')
            
            month_expense = db.query(func.sum(Bill.total_amount)).filter(
                Bill.user_id == user_id,
                Bill.billing_month == month,
                Bill.status.in_([BillStatus.PENDING, BillStatus.PAID])
            ).scalar() or Decimal('0')
            
            monthly_comparison.append({
                'month': month.strftime('%b/%Y'),
                'income': float(month_income),
                'expense': float(month_expense),
                'balance': float(month_income - month_expense)
            })
        
        return {
            'current_month': billing_month.strftime('%Y-%m'),
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'paid_expenses': float(paid_expenses),
            'pending_expenses': float(pending_expenses),
            'balance': float(total_income - total_expenses),
            'credit_cards': {
                'total_limit': float(total_credit_limit),
                'used_limit': float(total_used_limit),
                'available_limit': float(total_credit_limit - total_used_limit),
                'usage_percentage': round(float(total_used_limit / total_credit_limit * 100), 1) if total_credit_limit > 0 else 0
            },
            'upcoming_bills': [
                {
                    'id': bill.id,
                    'description': bill.description,
                    'amount': float(bill.total_amount),
                    'due_date': bill.due_date.isoformat(),
                    'category': bill.category.name if bill.category else None,
                    'category_color': bill.category.color if bill.category else None,
                    'card_name': bill.card.name if bill.card else None,
                    'installments': f"{bill.current_installment}/{bill.installments}" if bill.installments > 1 else None
                }
                for bill in upcoming_bills
            ],
            'top_categories': [
                {
                    'name': cat[0],
                    'color': cat[1],
                    'total': float(cat[2]),
                    'percentage': round(float(cat[2] / total_expenses * 100), 1) if total_expenses > 0 else 0
                }
                for cat in top_categories
            ],
            'monthly_comparison': monthly_comparison
        }