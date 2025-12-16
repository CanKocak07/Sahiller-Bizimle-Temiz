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
3. (Optional) Set `VITE_API_BASE_URL` in `.env.local` if your backend is not `http://127.0.0.1:8000`
4. Run the app:
   `npm run dev`
