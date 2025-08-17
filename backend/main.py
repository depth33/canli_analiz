import os, time, requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (gerekirse prod domainini yaz: ["https://canli-analiz.vercel.app"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY  = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

def _hdr():
    return {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

# ---- Basit bellek içi cache ----
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

def cache_set(key: str, data: dict):
    _CACHE[key] = (time.time(), data)

def remember_rate_headers(resp: requests.Response):
    # RapidAPI / API-Football bazı başlıklar döner; gördüklerimizi saklayalım
    global _LAST_RATELIMIT_HEADERS
    keep = {}
    for k, v in resp.headers.items():
        lk = k.lower()
        if "ratelimit" in lk or "limit" in lk:
            keep[k] = v
    if keep:
        _LAST_RATELIMIT_HEADERS = keep

@app.get("/")
def root():
    return {"status": "Backend çalışıyor ✅"}

@app.get("/quota")
def quota():
    """Son görülen rate-limit başlıkları (izleme amaçlı)."""
    return {"rate_limit_headers": _LAST_RATELIMIT_HEADERS}

# 👉 Sadece takım adına göre (CANLI) arama: live=all bir kez çekilir, takım adıyla filtrelenir
@app.get("/match-by-team")
def match_by_team(team: str = Query(..., description="Takım adı")):
    key = "live_all"  # tek kaynak: fixtures?live=all
    live_data = cache_get(key, ttl=60)

    if not live_data:
        url = f"{BASE_URL}/fixtures"
        params = {"live": "all"}
        try:
            resp = requests.get(url, headers=_hdr(), params=params, timeout=12)
            remember_rate_headers(resp)

            # 429 ise: cache varsa cache'ten dön, yoksa net hata ver
            if resp.status_code == 429:
                cached = cache_get(key, ttl=300)
                if cached:
                    live_data = cached
                    served_from = "cache_due_to_429"
                else:
                    return {
                        "error": "rate_limited",
                        "status_code": 429,
                        "message": "API limiti aşıldı. Biraz sonra tekrar deneyin.",
                        "rate_limit": _LAST_RATELIMIT_HEADERS
                    }
            elif resp.status_code != 200:
                return {
                    "error": "upstream_error",
                    "status_code": resp.status_code,
                    "body": _safe_body(resp)
                }
            else:
                live_data = resp.json()
                cache_set(key, live_data)
                served_from = "api"
        except Exception as e:
            # Ağ hatası vs. varsa ve cache varsa cache'ten dön
            cached = cache_get(key, ttl=300)
            if cached:
                live_data = cached
                served_from = "cache_due_to_exception"
            else:
                return {"error": "request_failed", "message": str(e)}

    else:
        served_from = "cache"

    # canlı veri yoksa
    resp_list = live_data.get("response", [])
    if not resp_list:
        return {"message": "Şu anda canlı maç bulunmuyor.", "source": served_from}

    # takım adına göre filtrele
    team_lower = team.lower()
    filtered = []
    for m in resp_list:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        if team_lower in home.lower() or team_lo
