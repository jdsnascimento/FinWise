"""
Testes de criação de contas (parceladas).
Requer DATABASE_URL no ambiente (ex.: .env do backend).
Execute: pytest test_create_bill.py -v
"""
import os
import sys
from decimal import Decimal
from datetime import date

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL não configurada",
)

from app.database import SessionLocal
from app.services.bill_service import BillService
from app.schemas.bill import BillCreate, PaymentTypeEnum


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_installment_bill(db):
    """Cria compra parcelada no cartão (dados de teste fixos no banco local)."""
    bill_data = BillCreate(
        description="Compra parcelada teste pytest",
        amount=Decimal("150.00"),
        installments=3,
        purchase_date=date.today(),
        category_id=1,
        card_id=1,
        payment_type=PaymentTypeEnum.CREDIT_CARD,
        notes="Teste pytest",
    )
    result = BillService.create_bill(db, user_id=1, bill_data=bill_data)
    assert result.id is not None
    assert result.installments == 3
