from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from typing import List, Optional

from ..models.bill import Bill, BillStatus, PaymentType
from ..models.income import Income, IncomeStatus
from ..models.credit_card import CreditCard
from ..models.category import Category

class ReportService:
    
    @staticmethod
    def get_expense_by_category(db: Session, user_id: int, 
                                 start_date: date, end_date: date):
        """Relatório de gastos por categoria"""
        results = db.query(
            Category.name,
            Category.color,
            func.sum(Bill.total_amount).label('total'),
            func.count(Bill.id).label('count')
        ).join(Bill).filter(
            Bill.user_id == user_id,
            Bill.status.in_([BillStatus.PENDING, BillStatus.PAID]),
            Bill.purchase_date >= start_date,
            Bill.purchase_date <= end_date
        ).group_by(Category.id).order_by(func.sum(Bill.total_amount).desc()).all()
        
        total = sum(r[2] for r in results) or Decimal('1')
        
        return [{
            'category': r[0],
            'color': r[1],
            'total': float(r[2] or 0),
            'count': r[3],
            'percentage': round(float((r[2] or 0) / total * 100), 1)
        } for r in results]
    
    @staticmethod
    def get_expense_by_card(db: Session, user_id: int,
                            start_date: date, end_date: date):
        """Relatório de gastos por cartão"""
        results = db.query(
            CreditCard.name,
            CreditCard.flag,
            CreditCard.color,
            func.sum(Bill.total_amount).label('total'),
            func.count(Bill.id).label('count')
        ).join(Bill).filter(
            Bill.user_id == user_id,
            Bill.card_id.isnot(None),
            Bill.status.in_([BillStatus.PENDING, BillStatus.PAID]),
            Bill.purchase_date >= start_date,
            Bill.purchase_date <= end_date
        ).group_by(CreditCard.id).order_by(func.sum(Bill.total_amount).desc()).all()
        
        return [{
            'card_name': r[0],
            'flag': r[1],
            'color': r[2],
            'total': float(r[3] or 0),
            'count': r[4]
        } for r in results]
    
    @staticmethod
    def get_monthly_evolution(db: Session, user_id: int, months: int = 12):
        """Evolução mensal de receitas e despesas"""
        evolution = []
        today = date.today()
        
        for i in range(months - 1, -1, -1):
            month_date = today.replace(day=1) - relativedelta(months=i)
            month_end = month_date.replace(
                day=calendar.monthrange(month_date.year, month_date.month)[1]
            )
            
            # Receitas
            income = db.query(func.sum(Income.amount)).filter(
                Income.user_id == user_id,
                Income.status == IncomeStatus.RECEIVED,
                Income.received_date >= month_date,
                Income.received_date <= month_end
            ).scalar() or Decimal('0')
            
            # Despesas
            expense = db.query(func.sum(Bill.total_amount)).filter(
                Bill.user_id == user_id,
                Bill.status.in_([BillStatus.PENDING, BillStatus.PAID]),
                Bill.billing_month == month_date
            ).scalar() or Decimal('0')
            
            evolution.append({
                'month': month_date.strftime('%Y-%m'),
                'month_name': month_date.strftime('%b/%Y'),
                'income': float(income),
                'expense': float(expense),
                'balance': float(income - expense),
                'savings_rate': round(float((income - expense) / income * 100), 1) if income > 0 else 0
            })
        
        return evolution
    
    @staticmethod
    def get_payment_methods_analysis(db: Session, user_id: int,
                                     start_date: date, end_date: date):
        """Análise por método de pagamento"""
        results = db.query(
            Bill.payment_type,
            func.sum(Bill.total_amount).label('total'),
            func.count(Bill.id).label('count')
        ).filter(
            Bill.user_id == user_id,
            Bill.status.in_([BillStatus.PENDING, BillStatus.PAID]),
            Bill.purchase_date >= start_date,
            Bill.purchase_date <= end_date
        ).group_by(Bill.payment_type).all()
        
        total = sum(float(r[1] or 0) for r in results) or 1
        
        payment_names = {
            'credit_card': 'Cartão de Crédito',
            'debit_card': 'Cartão de Débito',
            'pix': 'PIX',
            'cash': 'Dinheiro',
            'boleto': 'Boleto',
            'transfer': 'Transferência'
        }
        
        return [{
            'method': r[0],
            'method_name': payment_names.get(r[0], r[0]),
            'total': float(r[1] or 0),
            'count': r[2],
            'percentage': round(float(r[1] or 0) / total * 100, 1)
        } for r in results]
    
    @staticmethod
    def get_category_trends(db: Session, user_id: int, category_id: int, months: int = 6):
        """Tendência de gastos de uma categoria específica"""
        trends = []
        today = date.today()
        
        for i in range(months - 1, -1, -1):
            month_date = today.replace(day=1) - relativedelta(months=i)
            month_end = month_date.replace(
                day=calendar.monthrange(month_date.year, month_date.month)[1]
            )
            
            total = db.query(func.sum(Bill.total_amount)).filter(
                Bill.user_id == user_id,
                Bill.category_id == category_id,
                Bill.status.in_([BillStatus.PENDING, BillStatus.PAID]),
                Bill.purchase_date >= month_date,
                Bill.purchase_date <= month_end
            ).scalar() or Decimal('0')
            
            trends.append({
                'month': month_date.strftime('%b/%Y'),
                'total': float(total)
            })
        
        return trends

    @staticmethod
    def get_full_report(db: Session, user_id: int, 
                       start_date: date, end_date: date,
                       report_type: str = 'complete'):
        """Relatório completo consolidado"""
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {},
            'categories': [],
            'cards': [],
            'payment_methods': [],
            'monthly_evolution': []
        }
        
        # Resumo do período
        total_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.status == IncomeStatus.RECEIVED,
            Income.received_date >= start_date,
            Income.received_date <= end_date
        ).scalar() or Decimal('0')
        
        total_expense = db.query(func.sum(Bill.total_amount)).filter(
            Bill.user_id == user_id,
            Bill.status.in_([BillStatus.PENDING, BillStatus.PAID]),
            Bill.purchase_date >= start_date,
            Bill.purchase_date <= end_date
        ).scalar() or Decimal('0')
        
        paid_expense = db.query(func.sum(Bill.total_amount)).filter(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PAID,
            Bill.purchase_date >= start_date,
            Bill.purchase_date <= end_date
        ).scalar() or Decimal('0')
        
        report['summary'] = {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'paid_expense': float(paid_expense),
            'pending_expense': float(total_expense - paid_expense),
            'balance': float(total_income - total_expense),
            'savings_rate': round(float((total_income - total_expense) / total_income * 100), 1) if total_income > 0 else 0,
            'total_transactions': db.query(Bill).filter(
                Bill.user_id == user_id,
                Bill.purchase_date >= start_date,
                Bill.purchase_date <= end_date
            ).count()
        }
        
        # Dados detalhados
        report['categories'] = ReportService.get_expense_by_category(db, user_id, start_date, end_date)
        report['cards'] = ReportService.get_expense_by_card(db, user_id, start_date, end_date)
        report['payment_methods'] = ReportService.get_payment_methods_analysis(db, user_id, start_date, end_date)
        
        return report