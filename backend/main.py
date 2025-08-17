import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://canli-analiz.vercel.app"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Test endpoint
@app.get("/")
def read_root():
    return {"status": "Backend çalışıyor 🚀"}

# ✅ SofaScore canlı maçları çek
@app.get("/live-matches")
def live_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.json()

