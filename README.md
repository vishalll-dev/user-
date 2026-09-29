# Fake Users App (FastAPI + Frontend)

## Local run
    pip install -r requirements.txt
    python -m uvicorn main:app --reload
Open http://127.0.0.1:8000  (API docs: /docs)

## Render deploy
1. Ye folder GitHub par push karein.
2. Render > New > Web Service > repo select karein
   (ya New > Blueprint, render.yaml auto detect ho jayega).
3. Build: `pip install -r requirements.txt`
   Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy ke baad URL kholein.

## Keep-alive (sleep se bachav)
- Backend khud har 10 min /health ko ping karta hai (RENDER_EXTERNAL_URL se).
- Extra safe rehne ke liye UptimeRobot / cron-job.org par
  https://YOUR-APP.onrender.com/health ko 10 min interval par add karein.
