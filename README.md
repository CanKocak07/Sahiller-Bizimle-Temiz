<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/drive/1N7uEjHVdchM6_Nz9Y4vEKToJ34BIjX-c

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Start the backend (FastAPI) and set `OPENAI_API_KEY` in its environment (server-side)
   - Option A (recommended, no files): export in terminal
       - IMPORTANT: `export` must be in the SAME terminal session where you start `uvicorn` (env vars are not shared across terminals)
       - `export OPENAI_API_KEY="..."`
   - Option B (local file): copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY`
   - Run backend:
     - `cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
     - `uvicorn app.main:app --reload --port 8000`
3. (Optional) Set `VITE_API_BASE_URL` in `.env.local` if your backend is not `http://127.0.0.1:8000`
4. Run the app:
   `npm run dev`

### (Optional) Test AI endpoint

`curl -sS -X POST "http://127.0.0.1:8000/api/ai/beach-report" \
  -H "Content-Type: application/json" \
   -d '{"beach":{"name":"Konyaaltı","wqi":72,"temperature_c":25,"pollution_percent":18,"no2_mol_m2":0.00004,"air_quality":"moderate"}}' | cat`

If you run backend on a different port (e.g. `8001`), update both URLs accordingly (and set `VITE_API_BASE_URL`).

## Deploy (Cloud Run - single service)

This project can be deployed as a single Cloud Run service that serves both the frontend and the backend.

```zsh
gcloud config set project sahiller-bizimle-temiz-481410
gcloud config set run/region europe-west1

gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# If you want form submissions to persist in Cloud Run, use Firestore:
gcloud services enable firestore.googleapis.com

gcloud artifacts repositories create sahiller-repo --repository-format=docker --location=europe-west1
gcloud auth configure-docker europe-west1-docker.pkg.dev

docker build -t europe-west1-docker.pkg.dev/sahiller-bizimle-temiz-481410/sahiller-repo/sahiller:1 .
docker push europe-west1-docker.pkg.dev/sahiller-bizimle-temiz-481410/sahiller-repo/sahiller:1

gcloud run deploy sahiller \
   --image europe-west1-docker.pkg.dev/sahiller-bizimle-temiz-481410/sahiller-repo/sahiller:1 \
   --allow-unauthenticated \
   --port 8080 \
   --set-env-vars FORMS_STORAGE=firestore,FIRESTORE_PROJECT=sahiller-bizimle-temiz-481410

# Then set secrets in Cloud Run UI (recommended):
# - OPENAI_API_KEY
# - (optional) OPENAI_MODEL
```

### Forms + Database

- Volunteer and newsletter forms are stored in a SQLite DB by default (local/dev).
- DB file location (SQLite): `DB_PATH` env (default: `backend/data/app.db`).
- For Cloud Run, SQLite is not persistent. Use Firestore by setting:
   - `FORMS_STORAGE=firestore`
   - (optional) `FIRESTORE_PROJECT=sahiller-bizimle-temiz-481410`
- API endpoints:
   - `POST /api/forms/volunteer`
   - `POST /api/forms/newsletter`
