import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Frontend'ine CORS izni
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

@app.get("/live-matches")
def live_matches():
    """
    RapidAPI ürününü ENV ile seç:
    - RAPIDAPI_KEY : zorunlu (sen ekledin)
    - RAPIDAPI_HOST: seçtiğin ürünün host'u
    - RAPIDAPI_URL : çağrılacak endpoint (tam URL)
    """

    api_key = os.getenv("RAPIDAPI_KEY")
    api_host = os.getenv("RAPIDAPI_HOST")
    api_url  = os.getenv("RAPIDAPI_URL")

    if not api_key:
        return {"error": "RAPIDAPI_KEY eksik (Render > Environment'a ekleyin)."}

    if not api_host or not api_url:
        # Varsayılan olarak API-FOOTBALL'u deneriz (kart ister)
        api_host = api_host or "api-football-v1.p.rapidapi.com"
        api_url  = api_url  or "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }

    try:
        res = requests.get(api_url, headers=headers, timeout=15)
        # 200 değilse bile 500 atma; status + body'yi şeffaf döndür
        return {
            "status_code": res.status_code,
            "ok": res.ok,
            "host": api_host,
            "url": api_url,
            "body": safe_json(res)
        }
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}


def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return resp.text


