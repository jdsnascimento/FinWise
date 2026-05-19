"""
Job scheduler para tarefas automáticas
Execute separadamente ou integre ao startup
"""
# pyrefly: ignore [missing-import]
from apscheduler.schedulers.background import BackgroundScheduler
from .database import SessionLocal
from .services.notification_service import NotificationService

scheduler = BackgroundScheduler()

def check_bills_job():
    """Job diário para verificar vencimentos"""
    db = SessionLocal()
    try:
        notifications = NotificationService.check_upcoming_bills(db)
        print(f"✅ {len(notifications)} contas próximas do vencimento")
        # Aqui você enviaria notificações push/email/WhatsApp
    except Exception as e:
        print(f"❌ Erro no job de notificações: {e}")
    finally:
        db.close()

def check_limits_job():
    """Job para verificar limites dos cartões"""
    db = SessionLocal()
    try:
        alerts = NotificationService.check_card_limits(db)
        if alerts:
            print(f"⚠️ {len(alerts)} alertas de limite de cartão")
    except Exception as e:
        print(f"❌ Erro no job de limites: {e}")
    finally:
        db.close()

def start_scheduler():
    """Inicia jobs agendados"""
    # Verificar vencimentos todo dia às 8h
    scheduler.add_job(check_bills_job, 'cron', hour=8, minute=0)
    
    # Verificar limites a cada 6 horas
    scheduler.add_job(check_limits_job, 'interval', hours=6)
    
    scheduler.start()
    print("📅 Scheduler iniciado!")