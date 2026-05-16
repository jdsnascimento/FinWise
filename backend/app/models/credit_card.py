from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class CreditCard(Base):
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, comment="Nome/apelido do cartão")
    bank = Column(String(50), nullable=False, comment="Banco emissor")
    flag = Column(String(30), nullable=False, comment="Bandeira: Visa, Mastercard, etc")
    limit_amount = Column(Numeric(15, 2), nullable=False, comment="Limite total do cartão")
    available_limit = Column(Numeric(15, 2), nullable=False, comment="Limite disponível calculado")
    closing_day = Column(Integer, nullable=False, comment="Dia do fechamento da fatura (1-31)")
    due_day = Column(Integer, nullable=False, comment="Dia do vencimento da fatura (1-31)")
    color = Column(String(7), default="#6366f1", comment="Cor para identificação visual")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="credit_cards")
    bills = relationship("Bill", back_populates="card")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('closing_day BETWEEN 1 AND 31', name='check_closing_day'),
        CheckConstraint('due_day BETWEEN 1 AND 31', name='check_due_day'),
        CheckConstraint('limit_amount > 0', name='check_limit_positive'),
    )
    
    def __repr__(self):
        return f"<CreditCard(id={self.id}, name='{self.name}', bank='{self.bank}')>"