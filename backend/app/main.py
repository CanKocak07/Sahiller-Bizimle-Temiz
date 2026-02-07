"""
FastAPI application entry point.

Bu dosya:
- Backend uygulamasını başlatır
- Earth Engine'i initialize eder
- Temel health-check endpoint sağlar
"""

import asyncio
import importlib.metadata as _importlib_metadata
import os
from pathlib import Path

# Some dependencies (and/or reload tooling) may rely on importlib.metadata.packages_distributions,
# which is not available on Python < 3.10. Provide a best-effort shim for local dev.
if not hasattr(_importlib_metadata, "packages_distributions"):
    try:
        import importlib_metadata as _importlib_metadata_backport  # type: ignore

        _importlib_metadata.packages_distributions = _importlib_metadata_backport.packages_distributions  # type: ignore[attr-defined]
    except Exception:
        pass

try:
    from dotenv import load_dotenv

    # Load local env files if present. Safe in prod (no-op if missing).
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env.local"), override=False)
except Exception:
    # dotenv is optional; environment variables may be provided by the host.
    pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config.ee import initialize_earth_engine
from app.api.metrics import router as metrics_router
from app.api.ai import router as ai_router
from app.api.forms import router as forms_router
from app.api.forms import _init_db as init_forms_db
from app.services.daily_refresh_loop import daily_refresh_loop

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

    # Ensure local DB tables exist for form submissions.
    # (APIRouter startup hooks may not run in every hosting setup.)
    init_forms_db()

    # Prewarm cache windows so the whole site updates automatically.
    # Daily refresh loop is best-effort; for production, prefer Cloud Scheduler
    # calling /api/metrics/admin/refresh at 00:00 TR.
    try:
        days = int(os.getenv("REFRESH_DAYS", "7"))
    except ValueError:
        days = 7
    try:
        revise_days = int(os.getenv("REFRESH_REVISE_DAYS", "5"))
    except ValueError:
        revise_days = 5
    asyncio.create_task(daily_refresh_loop(days=days, revise_days=revise_days))

app.include_router(metrics_router)
app.include_router(ai_router)
app.include_router(forms_router)

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

# In Cloud Run we can serve the built frontend from backend/static (copied by Dockerfile).
# IMPORTANT: add this AFTER /api routes, otherwise it would intercept them.
_static_dir = Path(__file__).resolve().parents[1] / "static"
_index_html = _static_dir / "index.html"
if _static_dir.exists() and _index_html.exists():
    @app.get("/")
    def web_index():
        return FileResponse(str(_index_html))

    # SPA + static file handler: serve file if it exists, otherwise fallback to index.html
    @app.get("/{full_path:path}")
    def web_fallback(full_path: str):
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(status_code=404, detail="Not Found")

        candidate = (_static_dir / full_path).resolve()
        # Prevent path traversal
        if _static_dir not in candidate.parents and candidate != _static_dir:
            raise HTTPException(status_code=404, detail="Not Found")

        if candidate.exists() and candidate.is_file():
            return FileResponse(str(candidate))

        return FileResponse(str(_index_html))
