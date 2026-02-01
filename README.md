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
  -d '{"beach":{"name":"Konyaaltı","wqi":72,"temperature_c":25,"occupancy":0.4,"pollution_percent":18}}' | cat`

If you run backend on a different port (e.g. `8001`), update both URLs accordingly (and set `VITE_API_BASE_URL`).
