import os, requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://canli-analiz.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backend çalışıyor 🚀"}

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return resp.text

@app.get("/env-check")
def env_check():
    key = os.getenv("RAPIDAPI_KEY") or ""
    host = os.getenv("RAPIDAPI_HOST")
    url  = os.getenv("RAPIDAPI_URL")
    # key'i maskele
    masked = (key[:4] + "..." + key[-4:]) if key else None
    return {"RAPIDAPI_KEY(masked)": masked, "RAPIDAPI_HOST": host, "RAPIDAPI_URL": url}

@app.get("/live-matches")
def live_matches():
    api_key = os.getenv("RAPIDAPI_KEY")
    api_host = os.getenv("RAPIDAPI_HOST")
    api_url  = os.getenv("RAPIDAPI_URL")

    if not api_key:
        return {"error": "RAPIDAPI_KEY eksik (Render > Environment)"}
    if not api_host or not api_url:
        return {"error": "RAPIDAPI_HOST veya RAPIDAPI_URL eksik"}

    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": api_host}
    try:
        res = requests.get(api_url, headers=headers, timeout=15)
        return {
            "status_code": res.status_code,
            "ok": res.ok,
            "host": api_host,
            "url": api_url,
            "body": safe_json(res),
        }
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}
