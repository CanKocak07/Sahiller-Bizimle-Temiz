from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field


router = APIRouter(prefix="/api/forms", tags=["forms"])


def _forms_storage() -> str:
    # sqlite (local/dev) or firestore (Cloud Run recommended)
    return os.getenv("FORMS_STORAGE", "sqlite").strip().lower()


def _firestore_project() -> Optional[str]:
    return os.getenv("FIRESTORE_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")


def _get_firestore_client():
    try:
        from google.cloud import firestore  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firestore client not available: {e}")

    project = _firestore_project()
    return firestore.Client(project=project) if project else firestore.Client()


def _db_path() -> str:
    # Prefer explicit DB_PATH. Default to backend/data/app.db (easy to mount as volume).
    default_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "app.db")
    return os.getenv("DB_PATH", default_path)


def _connect() -> sqlite3.Connection:
    db_path = _db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    # timeout helps avoid 'database is locked' on brief concurrent writes.
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row

    # Reasonable defaults for a small demo app.
    # WAL improves concurrent read/write behavior.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS volunteer_signups (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              ip TEXT,
              user_agent TEXT,
              name TEXT NOT NULL,
              email TEXT NOT NULL,
              phone TEXT NOT NULL,
              beach_id TEXT NOT NULL,
              preferred_date TEXT NOT NULL,
              message TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS newsletter_signups (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              ip TEXT,
              user_agent TEXT,
              email TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


class VolunteerSignupIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=3, max_length=50)
    beachId: str = Field(min_length=1, max_length=64)
    date: str = Field(min_length=4, max_length=32)
    message: Optional[str] = Field(default=None, max_length=2000)


class NewsletterSignupIn(BaseModel):
    email: EmailStr


@router.on_event("startup")
def _startup_init_db() -> None:
    if _forms_storage() == "sqlite":
        _init_db()


@router.post("/volunteer")
def create_volunteer_signup(payload: VolunteerSignupIn, request: Request):
    storage = _forms_storage()
    if storage == "firestore":
        try:
            client = _get_firestore_client()
            now = datetime.now(timezone.utc).isoformat()
            doc = {
                "created_at": now,
                "ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "name": payload.name,
                "email": str(payload.email),
                "phone": payload.phone,
                "beach_id": payload.beachId,
                "preferred_date": payload.date,
                "message": payload.message,
            }
            client.collection("volunteer_signups").add(doc)
            return {"ok": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Firestore error: {e}")

    try:
        conn = _connect()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO volunteer_signups (
              created_at, ip, user_agent, name, email, phone, beach_id, preferred_date, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now,
                request.client.host if request.client else None,
                request.headers.get("user-agent"),
                payload.name,
                str(payload.email),
                payload.phone,
                payload.beachId,
                payload.date,
                payload.message,
            ),
        )
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return {"ok": True}


@router.post("/newsletter")
def create_newsletter_signup(payload: NewsletterSignupIn, request: Request):
    storage = _forms_storage()
    if storage == "firestore":
        try:
            client = _get_firestore_client()
            now = datetime.now(timezone.utc).isoformat()
            email_key = str(payload.email).strip().lower()
            ref = client.collection("newsletter_signups").document(email_key)

            # create() fails if already exists (gives us idempotency like UNIQUE).
            try:
                ref.create(
                    {
                        "created_at": now,
                        "ip": request.client.host if request.client else None,
                        "user_agent": request.headers.get("user-agent"),
                        "email": email_key,
                    }
                )
                created = True
            except Exception as e:
                # Firestore raises AlreadyExists; don't depend on class import.
                msg = str(e)
                created = False if ("AlreadyExists" in msg or "already exists" in msg) else False

            return {"ok": True, "created": created}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Firestore error: {e}")

    try:
        conn = _connect()
        now = datetime.now(timezone.utc).isoformat()
        try:
            conn.execute(
                """
                INSERT INTO newsletter_signups (created_at, ip, user_agent, email)
                VALUES (?, ?, ?, ?)
                """,
                (
                    now,
                    request.client.host if request.client else None,
                    request.headers.get("user-agent"),
                    str(payload.email),
                ),
            )
            conn.commit()
            created = True
        except sqlite3.IntegrityError:
            # already subscribed
            created = False
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return {"ok": True, "created": created}
