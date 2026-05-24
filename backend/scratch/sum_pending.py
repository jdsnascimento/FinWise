import os
import sys

os.environ["DATABASE_URL"] = "mysql+pymysql://finwise_user:finwise_pass@localhost:3307/finwise_db"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.credit_card import CreditCard
from app.models.bill import Bill, BillStatus

def run():
    db = SessionLocal()
    try:
        card = db.query(CreditCard).filter(CreditCard.id == 1).first()
        print("Card Limit:", card.limit_amount)
        print("Card Available Limit:", card.available_limit)
        
        pending_bills = db.query(Bill).filter(
            Bill.card_id == 1,
            Bill.status.in_([BillStatus.PENDING, BillStatus.OVERDUE])
        ).all()
        
        print("\nPending/Overdue Bills on Card 1:")
        total = 0
        for b in pending_bills:
            safe_desc = b.description.encode('ascii', errors='replace').decode('ascii')
            print(f"- ID {b.id}: {safe_desc} | Amount: {b.amount} | Total: {b.total_amount} | Status: {b.status}")
            total += b.amount
        print("\nSum of pending/overdue bills:", total)
        print("Recalculated Available Limit:", card.limit_amount - total)
    finally:
        db.close()

if __name__ == "__main__":
    run()
