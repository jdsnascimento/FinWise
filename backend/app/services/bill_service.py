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
        Exemplo: cartão fecha dia 31
        - Compra 17/05 → vence em JUNHO (billing_month = 2026-06-01)
        - Compra 01/06 → vence em JULHO (billing_month = 2026-07-01)
        """
        if purchase_date.day <= closing_day:
            # A compra entra na fatura que fecha este mês e vence no mês seguinte
            next_month = purchase_date.replace(day=1) + relativedelta(months=1)
            return next_month
        else:
            # A compra entra na fatura do mês que vem e vence no mês seguinte a esse
            next_month = purchase_date.replace(day=1) + relativedelta(months=2)
            return next_month
    
    @staticmethod
    def calculate_due_date(billing_month: date, due_day: int) -> date:
        """Retorna o dia de vencimento no mês de cobrança (billing_month)"""
        last_day = calendar.monthrange(billing_month.year, billing_month.month)[1]
        actual_due_day = min(due_day, last_day)
        return billing_month.replace(day=actual_due_day)
    
    @staticmethod
    def create_bill(db: Session, user_id: int, bill_data: BillCreate):
        """Cria uma nova conta a pagar com geração automática de parcelas ou recorrência"""
        
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
        
        # Se for cartão de crédito, validar e calcular datas iniciais
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
            
            # Calcular mês da fatura e vencimento inicial
            billing_month = BillService.calculate_billing_month(
                bill_data.purchase_date, 
                card.closing_day
            )
            due_date = BillService.calculate_due_date(billing_month, card.due_day)
        else:
            # Para pagamentos à vista ou recorrentes normais, usar data atual ou fornecida
            billing_month = bill_data.purchase_date.replace(day=1)
            due_date = bill_data.due_date or bill_data.purchase_date
        
        first_bill = None
        
        if bill_data.installments > 1:
            # Compra parcelada ou recorrente - Criar N registros Bill independentes
            base_description = bill_data.description
            
            # O valor enviado (amount) representa o total. O valor de cada parcela é total / parcelas.
            total = Decimal(str(bill_data.amount))
            installments = bill_data.installments
            installment_amount = (total / installments).quantize(Decimal('0.01'))
            
            for i in range(bill_data.installments):
                installment_number = i + 1
                desc = f"{base_description} ({installment_number}/{bill_data.installments})"
                
                if bill_data.payment_type == PaymentType.CREDIT_CARD:
                    installment_billing = billing_month + relativedelta(months=i)
                    installment_due = BillService.calculate_due_date(installment_billing, card.due_day)
                else:
                    installment_billing = billing_month + relativedelta(months=i)
                    if bill_data.due_date:
                        installment_due = bill_data.due_date + relativedelta(months=i)
                    else:
                        installment_due = bill_data.purchase_date + relativedelta(months=i)
                
                # Ajusta a última parcela com o resto da divisão para fechar o total exato
                if i < installments - 1:
                    current_amount = installment_amount
                else:
                    current_amount = total - (installment_amount * (installments - 1))
                
                bill = Bill(
                    user_id=user_id,
                    card_id=bill_data.card_id,
                    category_id=bill_data.category_id,
                    description=desc,
                    amount=current_amount,
                    total_amount=current_amount,  # Cada parcela/mês tem seu total_amount igual a amount para somar perfeitamente nos relatórios mensais
                    installments=bill_data.installments,
                    current_installment=installment_number,
                    purchase_date=bill_data.purchase_date,
                    due_date=installment_due,
                    billing_month=installment_billing,
                    status=BillStatus.PENDING,
                    payment_type=bill_data.payment_type,
                    source=bill_data.source if hasattr(bill_data, 'source') else 'manual',
                    notes=bill_data.notes
                )
                db.add(bill)
                db.flush()  # Para obter o ID
                
                # Criar o BillInstallment correspondente para manter compatibilidade com o ORM e schemas
                installment = BillInstallment(
                    bill_id=bill.id,
                    installment_number=installment_number,
                    amount=current_amount,
                    due_date=installment_due,
                    billing_month=installment_billing,
                    status=BillStatus.PENDING
                )
                db.add(installment)
                
                if i == 0:
                    first_bill = bill
        else:
            # Compra à vista - 1 parcela normal
            bill = Bill(
                user_id=user_id,
                card_id=bill_data.card_id,
                category_id=bill_data.category_id,
                description=bill_data.description,
                amount=bill_data.amount,
                total_amount=bill_data.total_amount or bill_data.amount,
                installments=1,
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
            db.flush()
            
            installment = BillInstallment(
                bill_id=bill.id,
                installment_number=1,
                amount=bill_data.total_amount or bill_data.amount,
                due_date=due_date,
                billing_month=billing_month,
                status=BillStatus.PENDING
            )
            db.add(installment)
            first_bill = bill
        
        # Recalcular limite do cartão
        if bill_data.payment_type == PaymentType.CREDIT_CARD and bill_data.card_id:
            from .credit_card_service import CreditCardService
            CreditCardService.recalculate_available_limit(db, bill_data.card_id)
        
        db.commit()
        db.refresh(first_bill)
        
        return first_bill
    
    @staticmethod
    def mark_overdue_bills(db: Session, user_id: int) -> int:
        """Marca contas pendentes com vencimento passado como vencidas."""
        today = date.today()
        overdue_bills = db.query(Bill).filter(
            Bill.user_id == user_id,
            Bill.status == BillStatus.PENDING,
            Bill.due_date < today
        ).all()

        for bill in overdue_bills:
            bill.status = BillStatus.OVERDUE
            for installment in bill.installments_list:
                if installment.status == BillStatus.PENDING:
                    installment.status = BillStatus.OVERDUE

        if overdue_bills:
            db.commit()

        return len(overdue_bills)
    
    @staticmethod
    def get_user_bills(db: Session, user_id: int, filters: BillFilter = None):
        """Lista contas do usuário com filtros"""
        BillService.mark_overdue_bills(db, user_id)
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
        BillService.mark_overdue_bills(db, user_id)
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
        # Rastrear cartões possivelmente afetados
        affected_card_ids = set()
        if bill.card_id:
            affected_card_ids.add(bill.card_id)
            
        # Tratar alteração de status
        if bill_data.status == BillStatus.PAID and bill.status != BillStatus.PAID:
            bill.status = BillStatus.PAID
            bill.paid_at = datetime.utcnow()
            
            # Pagar todas as parcelas
            for installment in bill.installments_list:
                if installment.status == BillStatus.PENDING:
                    installment.status = BillStatus.PAID
                    installment.paid_at = datetime.utcnow()
        
        elif bill_data.status == BillStatus.CANCELLED and bill.status != BillStatus.CANCELLED:
            bill.status = BillStatus.CANCELLED
            
            # Cancelar todas as parcelas pendentes
            for installment in bill.installments_list:
                if installment.status == BillStatus.PENDING:
                    installment.status = BillStatus.CANCELLED
        
        # Atualizar outros campos
        update_data = bill_data.dict(exclude_unset=True, exclude={'status'})
        
        # Se alterou o valor da conta (amount)
        if 'amount' in update_data and update_data['amount'] is not None:
            new_amount = update_data['amount']
            bill.amount = new_amount
            bill.total_amount = new_amount
            for installment in bill.installments_list:
                installment.amount = new_amount
            del update_data['amount']
            if 'total_amount' in update_data:
                del update_data['total_amount']

        if 'due_date' in update_data and update_data['due_date'] is not None:
            for installment in bill.installments_list:
                installment.due_date = update_data['due_date']

        if 'category_id' in update_data and update_data['category_id'] is not None:
            category = db.query(Category).filter(
                Category.id == update_data['category_id'],
                Category.user_id == user_id,
                Category.type == 'expense',
                Category.active == True
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Categoria inválida ou não encontrada"
                )

        # Se alterou o cartão ou outras propriedades
        if 'card_id' in update_data:
            if update_data['card_id']:
                affected_card_ids.add(update_data['card_id'])

        for field, value in update_data.items():
            if value is not None:
                setattr(bill, field, value)
                
        db.flush()
        
        # Recalcular limite disponível dos cartões afetados
        if affected_card_ids:
            from .credit_card_service import CreditCardService
            for cid in affected_card_ids:
                CreditCardService.recalculate_available_limit(db, cid)
        
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
        
        card_id = bill.card_id
        
        db.delete(bill)
        db.flush()
        
        # Recalcular limite do cartão
        if card_id:
            from .credit_card_service import CreditCardService
            CreditCardService.recalculate_available_limit(db, card_id)
            
        db.commit()
        
        return {"message": "Conta excluída com sucesso"}    
    @staticmethod
    def get_bills_summary(db: Session, user_id: int, billing_month: date = None):
        """Retorna resumo financeiro"""
        BillService.mark_overdue_bills(db, user_id)
        if not billing_month:
            billing_month = date.today().replace(day=1)
        
        # Próximo vencimento (pendentes ou já vencidas)
        next_due = db.query(Bill).filter(
            Bill.user_id == user_id,
            Bill.status.in_([BillStatus.PENDING, BillStatus.OVERDUE])
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