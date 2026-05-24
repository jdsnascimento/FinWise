import os
import sys

# Set environment variable before importing database
os.environ["DATABASE_URL"] = "mysql+pymysql://finwise_user:finwise_pass@localhost:3307/finwise_db"

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.credit_card import CreditCard
from app.services.credit_card_service import CreditCardService

def fix_limits():
    db = SessionLocal()
    try:
        cards = db.query(CreditCard).all()
        print("=== AJUSTANDO LIMITES DE CARTAO DE CREDITO ===")
        for card in cards:
            old_available = card.available_limit
            CreditCardService.recalculate_available_limit(db, card.id)
            db.commit()
            db.refresh(card)
            print(f"Cartao: {card.name} ({card.bank})")
            print(f"  Limite Total: {card.limit_amount}")
            print(f"  Limite Disponivel Antigo: {old_available}")
            print(f"  Limite Disponivel Novo (Corrigido): {card.available_limit}")
            print("-" * 40)
        print("\nSUCCESS: Todos os limites de cartoes de credito foram sincronizados com sucesso!")
    except Exception as e:
        print(f"\nERROR: Erro durante o ajuste de limites: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_limits()
