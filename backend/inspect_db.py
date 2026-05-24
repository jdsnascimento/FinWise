from app.database import SessionLocal
from app.models.user import User
from app.models.whatsapp_instance import WhatsAppInstance
from app.models.credit_card import CreditCard

db = SessionLocal()
try:
    print("--- USERS ---")
    users = db.query(User).all()
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}")
        
    print("\n--- WHATSAPP INSTANCES ---")
    instances = db.query(WhatsAppInstance).all()
    for inst in instances:
        print(f"ID: {inst.id}, UserID: {inst.user_id}, Name: {inst.instance_name}, Phone: {inst.phone_number}, Status: {inst.connection_status}")
        
    print("\n--- CREDIT CARDS ---")
    cards = db.query(CreditCard).all()
    for c in cards:
        print(f"ID: {c.id}, UserID: {c.user_id}, Name: {c.name}, Bank: {c.bank}, Limit: {c.limit_amount}, Avail Limit: {c.available_limit}")

finally:
    db.close()
