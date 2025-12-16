"""
FastAPI application entry point.

Bu dosya:
- Backend uygulamasını başlatır
- Earth Engine'i initialize eder
- Temel health-check endpoint sağlar
"""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.ee import initialize_earth_engine
from app.api.metrics import router as metrics_router
from app.api.ai import router as ai_router
from app.services.prewarm import prewarm_loop

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
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    # Dev ortamında Vite portu doluysa 3001/3002 gibi otomatik artabilir.
    # Local geliştirmede bu regex localhost'un farklı portlarını da kabul eder.
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Uygulama ayağa kalkarken bir kez çalışır.
    Earth Engine bağlantısını burada başlatıyoruz.
    """
    initialize_earth_engine()

    # Prewarm 2-hour cache windows so the whole site updates
    # automatically on even-hour boundaries.
    asyncio.create_task(prewarm_loop(days=7))

app.include_router(metrics_router)
app.include_router(ai_router)

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
