from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import webhook  # Adicionar

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

# Rotas
app.include_router(webhook.router)  # Adicionar

@app.get("/")
async def root():
    return {
        "message": f"Bem-vindo ao {settings.APP_NAME}",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}