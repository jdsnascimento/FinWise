"""
Script para testar a criação das tabelas no banco
Execute: python test_models.py
"""
from app.database import init_db, SessionLocal
from app.models import User, Category, CreditCard, Bill

def test_database():
    print("🔄 Criando tabelas...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Testar criação de usuário
        print("📝 Criando usuário de teste...")
        user = User(
            name="Teste",
            email="teste@finwise.com",
            hashed_password="hash123"
        )
        db.add(user)
        db.commit()
        print(f"✅ Usuário criado: {user.email}")
        
        # Testar criação de categoria
        print("📝 Criando categoria...")
        category = Category(
            user_id=user.id,
            name="Alimentação",
            icon="restaurant",
            color="#ef4444",
            type="expense"
        )
        db.add(category)
        db.commit()
        print(f"✅ Categoria criada: {category.name}")
        
        # Testar criação de cartão
        print("📝 Criando cartão de crédito...")
        card = CreditCard(
            user_id=user.id,
            name="Nubank",
            bank="Nubank",
            flag="Mastercard",
            limit_amount=5000.00,
            available_limit=5000.00,
            closing_day=10,
            due_day=15,
            color="#8a05be"
        )
        db.add(card)
        db.commit()
        print(f"✅ Cartão criado: {card.name}")
        
        # Testar criação de conta
        print("📝 Criando conta a pagar...")
        bill = Bill(
            user_id=user.id,
            card_id=card.id,
            category_id=category.id,
            description="Compra mercado",
            amount=500.00,
            total_amount=1500.00,
            installments=3,
            current_installment=1,
            purchase_date="2024-01-20",
            due_date="2024-02-15",
            billing_month="2024-02-01",
            payment_type="credit_card",
            source="manual"
        )
        db.add(bill)
        db.commit()
        print(f"✅ Conta criada: {bill.description} ({bill.installment_label})")
        
        print("\n🎉 Banco de dados criado e testado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database()