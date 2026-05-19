from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .routes import auth, credit_cards, bills, incomes, categories, dashboard, whatsapp
from .routes import reports
from .routes import notifications



app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Controle Financeiro Pessoal com WhatsApp"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(auth.router)  # Rotas de autenticação
# Adicionar depois das rotas de auth
app.include_router(credit_cards.router)
# Adicionar rota
app.include_router(bills.router)
# Adicionar rotas
app.include_router(incomes.router)
app.include_router(categories.router)
app.include_router(dashboard.router)
# Adicionar rota
app.include_router(whatsapp.router)
# Rotas de relatórios
app.include_router(reports.router)
app.include_router(notifications.router)

@app.on_event("startup")
async def startup_event():
    """Inicializa banco de dados ao iniciar"""
    init_db()
    print("✅ Banco de dados inicializado com sucesso!")
    print("🚀 FinWise API pronta!")

@app.get("/")
async def root():
    return {
        "message": f"Bem-vindo ao {settings.APP_NAME}",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# No startup_event, adicionar:
@app.on_event("startup")
async def startup_event():
    init_db()
    # from .scheduler import start_scheduler
    # start_scheduler()  # Descomentar para ativar jobs
    print("🚀 FinWise API pronta!")
