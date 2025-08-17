import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS ayarları (sadece senin frontend domenine izin veriyoruz)
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

# ✅ Canlı maç listesini SofaScore'dan çek
@app.get("/live-matches")
def live_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    response = requests.get(url)
    return response.json()
