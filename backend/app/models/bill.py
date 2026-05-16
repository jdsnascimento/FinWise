from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class BillStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentType(str, enum.Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BOLETO = "boleto"
    TRANSFER = "transfer"

class BillSource(str, enum.Enum):
    MANUAL = "manual"
    WHATSAPP = "whatsapp"
    IMPORT = "import"

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey("credit_cards.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    
    # Informações da compra
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False, comment="Valor de cada parcela")
    total_amount = Column(Numeric(15, 2), nullable=False, comment="Valor total da compra")
    
    # Controle de parcelamento
    installments = Column(Integer, default=1, comment="Total de parcelas")
    current_installment = Column(Integer, default=1, comment="Parcela atual (1-based)")
    
    # Datas (AQUI ESTÁ O SEGREDO)
    purchase_date = Column(Date, nullable=False, comment="Data que a compra foi feita")
    due_date = Column(Date, nullable=False, comment="Data de vencimento DESTA parcela")
    billing_month = Column(Date, nullable=False, comment="Mês/ano de referência para fatura (ex: 2024-01-01)")
    
    # Status e tipo
    status = Column(Enum(BillStatus), default=BillStatus.PENDING)
    payment_type = Column(Enum(PaymentType), nullable=False)
    source = Column(Enum(BillSource), default=BillSource.MANUAL)
    
    # Controle
    paid_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="bills")
    card = relationship("CreditCard", back_populates="bills")
    category = relationship("Category")
    installments_list = relationship("BillInstallment", back_populates="bill", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bill(id={self.id}, description='{self.description}', amount={self.total_amount})>"
    
    @property
    def installment_label(self):
        """Retorna label da parcela ex: '1/3', '2/3'"""
        return f"{self.current_installment}/{self.installments}"
    
    @property
    def is_credit_card(self):
        """Verifica se é pagamento com cartão de crédito"""
        return self.payment_type == PaymentType.CREDIT_CARD