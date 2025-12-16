"""
FastAPI application entry point.

Bu dosya:
- Backend uygulamasını başlatır
- Earth Engine'i initialize eder
- Temel health-check endpoint sağlar
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.ee import initialize_earth_engine
from app.api.metrics import router as metrics_router

app = FastAPI(
    title="Sahiller Bizimle Temiz API",
    description="Satellite-based environmental indicators backend",
    version="0.1.0",
)

# Frontend (Vite) ile backend farklı origin'lerde çalıştığı için CORS gerekir.
# Prod ortamında allow_origins'i kendi domain'inizle kısıtlayın.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """
    Uygulama ayağa kalkarken bir kez çalışır.
    Earth Engine bağlantısını burada başlatıyoruz.
    """
    initialize_earth_engine()

app.include_router(metrics_router)

@app.get("/health")
def health_check():
    """
    Basit sağlık kontrolü.
    Frontend ve deploy testleri için kullanılır.
    """
    return {
        "status": "ok",
        "service": "backend",
        "earth_engine": "initialized"
    }
