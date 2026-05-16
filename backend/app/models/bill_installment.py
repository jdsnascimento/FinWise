from sqlalchemy import Column, Integer, Numeric, Date, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .bill import BillStatus

class BillInstallment(Base):
    __tablename__ = "bill_installments"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)
    installment_number = Column(Integer, nullable=False, comment="Número da parcela (1, 2, 3...)")
    amount = Column(Numeric(15, 2), nullable=False, comment="Valor desta parcela")
    due_date = Column(Date, nullable=False, comment="Data de vencimento desta parcela")
    billing_month = Column(Date, nullable=False, comment="Mês da fatura (2024-01-01)")
    status = Column(Enum(BillStatus), default=BillStatus.PENDING)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    bill = relationship("Bill", back_populates="installments_list")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('bill_id', 'installment_number', name='uk_bill_installment'),
    )
    
    def __repr__(self):
        return f"<BillInstallment(bill_id={self.bill_id}, num={self.installment_number}/{self.bill.installments if self.bill else '?'})>"