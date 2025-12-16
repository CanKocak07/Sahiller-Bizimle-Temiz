"""
FastAPI application entry point.

Bu dosya:
- Backend uygulamasını başlatır
- Earth Engine'i initialize eder
- Temel health-check endpoint sağlar
"""

from fastapi import FastAPI
from app.config.ee import initialize_earth_engine

app = FastAPI(
    title="Sahiller Bizimle Temiz API",
    description="Satellite-based environmental indicators backend",
    version="0.1.0",
)

@app.on_event("startup")
def startup_event():
    """
    Uygulama ayağa kalkarken bir kez çalışır.
    Earth Engine bağlantısını burada başlatıyoruz.
    """
    initialize_earth_engine()

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
