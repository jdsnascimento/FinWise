from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from ..models.bill import Bill, BillStatus, PaymentType
from ..models.bill_installment import BillInstallment
from ..models.credit_card import CreditCard
from ..models.category import Category
from ..schemas.bill import BillCreate, BillUpdate, BillFilter
from fastapi import HTTPException, status

class BillService:
    
    @staticmethod
    def calculate_billing_month(purchase_date: date, closing_day: int) -> date:
        """
        Determina o mês da fatura baseado na data da compra e fechamento do cartão
        
        Regra:
        - Compra antes ou no dia do fechamento → fatura MESMO mês
        - Compra depois do fechamento → fatura PRÓXIMO mês
        """
        if purchase_date.day <= closing_day:
            # Fatura do mês atual
            return purchase_date.replace(day=1)
        else:
            # Fatura do próximo mês
            return (purchase_date.replace(day=1) + relativedelta(months=1))
    
    @staticmethod
    def calculate_due_date(billing_month: date, due_day: int) -> date:
        """Calcula data de vencimento baseado no mês da fatura e dia de vencimento"""
        # Pegar último dia do mês
        last_day = calendar.monthrange(billing_month.year, billing_month.month)[1]
        actual_due_day = min(due_day, last_day)
        
        return billing_month.replace(day=actual_due_day)
    
    @staticmethod
    def create_bill(db: Session, user_id: int, bill_data: BillCreate):
        """Cria uma nova conta a pagar com geração automática de parcelas"""
        
        # Validar categoria
        category = db.query(Category).filter(
            Category.id == bill_data.category_id,
            Category.user_id == user_id,
            Category.type == 'expense'
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria inválida ou não encontrada"
            )
        
        # Se for cartão de crédito, validar e calcular datas
        card = None
        if bill_data.payment_type == PaymentType.CREDIT_CARD:
            if not bill_data.card_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cartão é obrigatório para pagamento com crédito"
                )
            
            card = db.query(CreditCard).filter(
                CreditCard.id == bill_data.card_id,
                CreditCard.user_id == user_id,
                CreditCard.active == True
            ).first()
            
            if not card:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cartão não encontrado ou inativo"
                )
            
            # Verificar limite disponível
            if bill_data.total_amount > card.available_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Limite insuficiente! Disponível: R$ {card.available_limit:,.2f}"
                )
            
            # Calcular mês da fatura e vencimento
            billing_month = BillService.calculate_billing_month(
                bill_data.purchase_date, 
                card.closing_day
            )
            due_date = BillService.calculate_due_date(billing_month, card.due_day)
        else:
            # Para pagamentos à vista, usar data atual ou data fornecida
            billing_month = bill_data.purchase_date.replace(day=1)
            due_date = bill_data.due_date or bill_data.purchase_date
        
        # Criar a conta principal
        bill = Bill(
            user_id=user_id,
            card_id=bill_data.card_id,
            category_id=bill_data.category_id,
            description=bill_data.description,
            amount=bill_data.amount,
            total_amount=bill_data.total_amount,
            installments=bill_data.installments,
            current_installment=1,
            purchase_date=bill_data.purchase_date,
            due_date=due_date,
            billing_month=billing_month,
            status=BillStatus.PENDING,
            payment_type=bill_data.payment_type,
            source=bill_data.source if hasattr(bill_data, 'source') else 'manual',
            notes=bill_data.notes
        )
        
        db.add(bill)
        db.flush()  # Para obter o ID
        
        # Criar parcelas
        installments_created = []
        
        if bill_data.installments > 1 and bill_data.payment_type == PaymentType.CREDIT_CARD:
            for i in range(bill_data.installments):
                installment_number = i + 1
                
                # Calcular mês da fatura para cada parcela
                installment_billing = billing_month + relativedelta(months=i)
                installment_due = BillService.calculate_due_date(
                    installment_billing, 
                    card.due_day
                )
                
                installment = BillInstallment(
                    bill_id=bill.id,
                    installment_number=installment_number,
                    amount=bill_data.amount,
                    due_date=installment_due,
                    billing_month=installment_billing,
                    status=BillStatus.PENDING
                )
                
                db.add(installment)
                installments_created.append({
                    'number': installment_number,
                    'due_date': installment_due,
                    'billing_month': installment_billing
                })
        else:
            # Compra à vista - 1 parcela
            installment = BillInstallment(
                bill_id=bill.id,
                installment_number=1,
                amount=bill_data.total_amount or bill_data.amount,
                due_date=due_date,
                billing_month=billing_month,
                status=BillStatus.PENDING
            )
            db.add(installment)
        
        # Atualizar limite do cartão
        if card:
            card.available_limit -= bill_data.total_amount
        
        db.commit()
        db.refresh(bill)
        
        return bill
    
    @staticmethod
    def get_user_bills(db: Session, user_id: int, filters: BillFilter = None):
        """Lista contas do usuário com filtros"""
        query = db.query(Bill).filter(Bill.user_id == user_id)
        
        if filters:
            if filters.status:
                query = query.filter(Bill.status == filters.status)
            if filters.category_id:
                query = query.filter(Bill.category_id == filters.category_id)
            if filters.card_id:
                query = query.filter(Bill.card_id == filters.card_id)
            if filters.payment_type:
                query = query.filter(Bill.payment_type == filters.payment_type)
            if filters.start_date:
                query = query.filter(Bill.due_date >= filters.start_date)
            if filters.end_date:
                query = query.filter(Bill.due_date <= filters.end_date)
            if filters.billing_month:
                query = query.filter(Bill.billing_month == filters.billing_month)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(Bill.description.ilike(search_term))
        
        # Ordenar por data de vencimento (próximos primeiro)
        query = query.order_by(Bill.due_date.asc())
        
        bills = query.all()
        
        # Adicionar informações relacionadas
        for bill in bills:
            if bill.category:
                bill.category_name = bill.category.name
                bill.category_color = bill.category.color
            if bill.card:
                bill.card_name = bill.card.name
        
        return bills
    
    @staticmethod
    def get_bill_by_id(db: Session, bill_id: int, user_id: int):
        """Busca conta específica"""
        bill = db.query(Bill).filter(
            Bill.id == bill_id,
            Bill.user_id == user_id
        ).first()
        
        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta não encontrada"
            )
        
        # Adicionar informações relacionadas
        if bill.category:
            bill.category_name = bill.category.name
            bill.category_color = bill.category.color
        if bill.card:
            bill.card_name = bill.card.name
        
        return bill
    
    @staticmethod
    def update_bill(db: Session, bill_id: int, user_id: int, bill_data: BillUpdate):
        """Atualiza conta existente"""
        bill = BillService.get_bill_by_id(db, bill_id, user_id)
        
        # Se estiver pagando a conta
        if bill_data.status == BillStatus.PAID and bill.status != BillStatus.PAID:
            bill.status = BillStatus.PAID
            bill.paid_at = datetime.utcnow()
            
            # Pagar todas as parcelas
            for installment in bill.installments_list:
                if installment.status == BillStatus.PENDING:
                    installment.status = BillStatus.PAID
                    installment.paid_at = datetime.utcnow()
            
            # Liberar limite do cartão
            if bill.card:
                bill.card.available_limit += bill.total_amount
        
        # Se estiver cancelando
        elif bill_data.status == BillStatus.CANCELLED and bill.status != BillStatus.CANCELLED:
            bill.status = BillStatus.CANCELLED
            
            # Cancelar todas as parcelas pendentes
            for installment in bill.installments_list:
                if installment.status == BillStatus.PENDING:
                    installment.status = BillStatus.CANCELLED
            
            # Liberar limite do cartão
            if bill.card and bill.status == BillStatus.PENDING:
                bill.card.available_limit += bill.total_amount
        
        # Atualizar outros campos
        update_data = bill_data.dict(exclude_unset=True, exclude={'status'})
        for field, value in update_data.items():
            if value is not None:
                setattr(bill, field, value)
        
        db.commit()
        db.refresh(bill)
        
        return bill
    
    @staticmethod
    def delete_bill(db: Session, bill_id: int, user_id: int):
        """Remove conta (só se estiver pendente)"""
        bill = BillService.get_bill_by_id(db, bill_id, user_id)
        
        if bill.status != BillStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas contas pendentes podem ser excluídas"
            )
        
        # Liberar limite do cartão
        if bill.card:
            bill.card.available_limit += bill.total_amount
        
        db.delete(bill)
        db.commit()
        
        return {"message": "Conta excluída com sucesso"}
    
    @staticmethod
    def get_bills_summary(db: Session, user_id: int, billing_month: date = None):
        """Retorna resumo financeiro"""
        if not billing_month:
            billing_month = date.today().replace(day=1)
        
        # Próximo vencimento
        next_due = db.query(Bill).filter(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING,
            Bill.due_date >= date.today()
        ).order_by(Bill.due_date.asc()).first()
        
        # Totais
        totals = db.query(
            func.sum(Bill.total_amount).label('total'),
            Bill.status
        ).filter(
            Bill.user_id == user_id,
            Bill.billing_month == billing_month
        ).group_by(Bill.status).all()
        
        summary = {
            'total_pending': Decimal('0'),
            'total_paid': Decimal('0'),
            'total_overdue': Decimal('0'),
            'pending_count': 0,
            'next_due': next_due.due_date if next_due else None,
            'next_due_amount': next_due.total_amount if next_due else Decimal('0')
        }
        
        for total in totals:
            if total.status == BillStatus.PENDING:
                summary['total_pending'] = total.total
            elif total.status == BillStatus.PAID:
                summary['total_paid'] = total.total
            elif total.status == BillStatus.OVERDUE:
                summary['total_overdue'] = total.total
        
        # Contar pendentes
        summary['pending_count'] = db.query(Bill).filter(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING,
            Bill.billing_month == billing_month
        ).count()
        
        return summary