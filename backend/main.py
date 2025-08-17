import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (frontend ile konuşabilmesi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-Football bilgileri
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "api-football-v1.p.rapidapi.com")
RAPIDAPI_URL = os.getenv("RAPIDAPI_URL", "https://api-football-v1.p.rapidapi.com/v3")


def get_headers():
    return {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }


@app.get("/")
def home():
    return {"status": "Backend çalışıyor", "api": "API-Football bağlı"}


# 1. Canlı maçlar
@app.get("/live-stats")
def live_stats():
    url = f"{RAPIDAPI_URL}/fixtures?live=all"
    response = requests.get(url, headers=get_headers(), timeout=15)
    return response.json()


# 2. Maç istatistikleri (fixture_id ile)
@app.get("/fixture-stats/{fixture_id}")
def fixture_stats(fixture_id: int):
    url = f"{RAPIDAPI_URL}/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=get_headers(), timeout=15)
    return response.json()


# 3. Maç olayları (goller, kartlar, değişiklikler)
@app.get("/fixture-events/{fixture_id}")
def fixture_events(fixture_id: int):
    url = f"{RAPIDAPI_URL}/fixtures/events?fixture={fixture_id}"
    response = requests.get(url, headers=get_headers(), timeout=15)
    return response.json()


# 4. Lig listesi (opsiyonel)
@app.get("/leagues")
def leagues():
    url = f"{RAPIDAPI_URL}/leagues"
    response = requests.get(url, headers=get_headers(), timeout=15)
    return response.json()
