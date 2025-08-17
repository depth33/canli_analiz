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

def cache_set(key: str, data: dict):
    _CACHE[key] = (time.time(), data)

def remember_rate_headers(resp: requests.Response):
    global _LAST_RATELIMIT_HEADERS
    keep = {}
    for k, v in resp.headers.items():
        lk = k.lower()
        if "ratelimit" in lk or lk.endswith("-limit") or "requests-remaining" in lk:
            keep[k] = v
    if keep:
        _LAST_RATELIMIT_HEADERS = keep

def _safe_body(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        return resp.text

# -------- Esnek takım adı eşleştirme --------
_PUNCT = re.compile(r"[^a-z0-9]+")
_STOP_TOKENS = {"sk","fk","cf","as","kulubu","kulubu","spor","fc","ac","sc","as","as."}

def normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = _PUNCT.sub(" ", s)
    tokens = [t for t in s.split() if t and t not in _STOP_TOKENS]
    return " ".join(tokens)

def score_str(m: dict) -> str:
    gh = m["goals"]["home"] if m["goals"]["home"] is not None else 0
    ga = m["goals"]["away"] if m["goals"]["away"] is not None else 0
    return f"{gh} - {ga}"

# -------- Sağlık / kota --------
@app.get("/")
def root():
    return {"status": "Backend çalışıyor ✅", "api": "API-Football"}

@app.get("/quota")
def quota():
    return {"rate_limit_headers": _LAST_RATELIMIT_HEADERS}

# -------- İç yardımcı: canlı fikstürleri getir (cache'li) --------
def fetch_live_fixtures():
    key = "live_all"
    live_data = cache_get(key, ttl=60)
    if live_data:
        return live_data, "cache"

    url = f"{BASE_URL}/fixtures"
    params = {"live": "all"}
    resp = requests.get(url, headers=_hdr(), params=params, timeout=12)
    remember_rate_headers(resp)

    if resp.status_code == 429:
        cached = cache_get(key, ttl=300)
        if cached:
            return cached, "cache_due_to_429"
        return {
            "error": "rate_limited",
            "status_code": 429,
            "message": "API limiti aşıldı. Biraz sonra tekrar deneyin.",
            "rate_limit": _LAST_RATELIMIT_HEADERS
        }, "error"
    if resp.status_code != 200:
        return {"error": "upstream_error", "status_code": resp.status_code, "body": _safe_body(resp)}, "error"

    live_data = resp.json()
    cache_set(key, live_data)
    return live_data, "api"

# -------- YENİ: Canlı maçları basit listede döndür --------
@app.get("/list-live")
def list_live():
    if not API_KEY:
        return {"error": "RAPIDAPI_KEY eksik (Render Environment'a ekleyin)"}
    data, source = fetch_live_fixtures()
    if isinstance(data, dict) and data.get("error"):
        return data
    lst = []
    for m in data.get("response", []):
        lst.append({
            "fixture_id": m["fixture"]["id"],
            "home": m["teams"]["home"]["name"],
            "away": m["teams"]["away"]["name"],
            "league": m["league"]["name"],
            "country": m["league"]["country"],
            "minute": m["fixture"]["status"]["elapsed"],
            "status": m["fixture"]["status"]["long"],
            "score": score_str(m),
            "tokens": {
                "home_norm": normalize(m["teams"]["home"]["name"]),
                "away_norm": normalize(m["teams"]["away"]["name"]),
            }
        })
    return {"count": len(lst), "source": source, "matches": lst}

# -------- Takım adına göre CANLI arama --------
@app.get("/match-by-team")
def match_by_team(team: str = Query(..., description="Takım adı (canlı maçlarda aranır)")):
    if not API_KEY:
        return {"error": "RAPIDAPI_KEY eksik (Render Environment'a ekleyin)"}
    data, source = fetch_live_fixtures()
    if isinstance(data, dict) and data.get("error"):
        return data

    resp_list = data.get("response", [])
    if not resp_list:
        return {"message": "Şu anda canlı maç bulunmuyor.", "source": source}

    q = normalize(team)
    results = []
    for m in resp_list:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        if q in normalize(home) or q in normalize(away):
            results.append({
                "fixture_id": m["fixture"]["id"],
                "league": m["league"]["name"],
                "country": m["league"]["country"],
                "home": home,
                "away": away,
                "score": score_str(m),
                "minute": m["fixture"]["status"]["elapsed"],
                "status": m["fixture"]["status"]["long"]
            })

    if not results:
        return {"message": f"{team} takımının şu anda canlı maçı yok.", "source": source}

    return {"results": results, "source": source}

# -------- İsteğe bağlı: Fixture ID ile tek maç --------
@app.get("/match-stats/{fixture_id}")
def match_stats(fixture_id: int):
    if not API_KEY:
        return {"error": "RAPIDAPI_KEY eksik"}
    url = f"{BASE_URL}/fixtures"
    params = {"id": fixture_id}
    resp = requests.get(url, headers=_hdr(), params=params, timeout=12)
    remember_rate_headers(resp)

    if resp.status_code == 429:
        return {
            "error": "rate_limited",
            "status_code": 429,
            "message": "API limiti aşıldı. Biraz sonra tekrar deneyin.",
            "rate_limit": _LAST_RATELIMIT_HEADERS
        }
    if resp.status_code != 200:
        return {"error": "upstream_error", "status_code": resp.status_code, "body": _safe_body(resp)}

    data = resp.json()
    if not data.get("response"):
        return {"message": "Bu ID için maç bulunamadı."}
    m = data["response"][0]
    return {
        "fixture_id": m["fixture"]["id"],
        "date": m["fixture"]["date"],
        "status": m["fixture"]["status"]["long"],
        "league": m["league"]["name"],
        "country": m["league"]["country"],
        "home_team": m["teams"]["home"]["name"],
        "away_team": m["teams"]["away"]["name"],
        "goals": {
            "home": m["goals"]["home"] if m["goals"]["home"] is not None else 0,
            "away": m["goals"]["away"] if m["goals"]["away"] is not None else 0
        }
    }
