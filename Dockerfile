# Multi-stage build: 1) build frontend, 2) run FastAPI backend on Cloud Run

# --- Frontend build ---
FROM node:20-alpine AS web
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build


# --- Backend runtime ---
FROM python:3.11-slim AS api
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

# Install backend deps
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source
COPY backend ./backend

# Copy built frontend into backend static directory
RUN mkdir -p ./backend/static
COPY --from=web /app/dist ./backend/static

# Cloud Run sets PORT; default 8080
ENV PORT=8080
EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
