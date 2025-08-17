import os, time, re, unicodedata, requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (istersen prod domainini yazabilirsin: ["https://canli-analiz.vercel.app"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- API-Football (RapidAPI) --------
API_KEY  = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

def _hdr():
    return {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

# -------- Basit cache + rate header takibi --------
_CACHE: dict[str, tuple[float, dict]] = {}
_LAST_RATELIMIT_HEADERS: dict[str, str] = {}

def cache_get(key: str, ttl: int = 60):
    item = _CACHE.get(key)
    if not item:
        return None
    ts, data = item
    if time.time() - ts <= ttl:
        return data
    return None

def cache_set(key: str, data: dict)_
