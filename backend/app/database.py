from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Importar todos os models para criar as tabelas
def init_db():
    from .models import (
        User,
        Category,
        CreditCard,
        Bill,
        BillInstallment,
        Income,
        WhatsAppInstance
    )
    Base.metadata.create_all(bind=engine)