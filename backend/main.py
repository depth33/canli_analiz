import os, time, re, unicodedata, requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (istersen prod alanını yazabilirsin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # örn: ["https://canli-analiz.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RapidAPI / API-Football
API_KEY  = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

def _hdr():
    return {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

# ---------------- Cache / Ratelimit Yardımcıları ----------------
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

# ---------------- Metin Normalizasyonu (esnek eşleşme) ----------------
_PUNCT = re.compile(r"[^a-z0-9]+")
_STOP_TOKENS = {
    "sk", "fk", "cf", "as", "a.s", "a.ş", "kulübü", "spor", "fc", "ac", "sc"
}

def normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    # Türkçe/aksan temizliği
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    # noktalama/boşluk sadeleştirme
    s = _PUNCT.sub(" ", s)
    tokens = [t for t in s.split() if t and t not in _STOP_TOKENS]
    return " ".join(tokens)

# ---------------- Sağlık / Kota ----------------
@app.get("/")
def root():
    return {"status": "Backend çalışıyor ✅", "api": "API-Football"}

@app.get("/quota")
def quota():
    return {"rate_limit_headers": _LAST_RATELIMIT_HEADERS}

# ---------------- CANLI: Takım adına göre arama ----------------
@app.get("/match-by-team")
def match_by_team(team: str = Query(..., description="Takım adı (canlı maçlarda aranır)")):
    if not API_KEY:
        return {"error": "RAPIDAPI_KEY eksik (Render Environment'a ekleyin)"}

    key = "live_all"
    live_data = cache_get(key, ttl=60)

    if not live_data:
        url = f"{BASE_URL}/fixtures"
        params = {"live": "all"}
        try:
            resp = requests.get(url, headers=_hdr(), params=params, timeout=12)
            remember_rate_headers(resp)

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
            cached = cache_get(key, ttl=300)
            if cached:
                live_data = cached
                served_from = "cache_due_to_exception"
            else:
                return {"error": "request_failed", "message": str(e)}
    else:
        served_from = "cache"

    resp_list = live_data.get("response", [])
    if not resp_list:
        return {"message": "Şu anda canlı maç bulunmuyor.", "source": served_from}

    q = normalize(team)
    results = []
    for m in resp_list:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        # esnek eşleşme (aksan + ünvan temizliği)
        if q in normalize(home) or q in normalize(away):
            results.append({
                "fixture_id": m["fixture"]["id"],
                "league": m["league"]["name"],
                "country": m["league"]["country"],
                "home": home,
                "away": away,
                "score": f'{m["goals"]["home"]} - {m["goals"]["away"]}',
                "minute": m["fixture"]["status"]["elapsed"],
                "status": m["fixture"]["status"]["long"]
            })

    if not results:
        return {"message": f"{team} takımının şu anda canlı maçı yok.", "source": served_from}

    return {"results": results, "source": served_from}

# ---------------- İsteğe bağlı: Fixture ID ile tek maç ----------------
@app.get("/match-stats/{fixture_id}")
def match_stats(fixture_id: int):
    if not API_KEY:
        return {"error": "RAPIDAPI_KEY eksik"}
    url = f"{BASE_URL}/fixtures"
    params = {"id": fixture_id}
    try:
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
            return {
                "error": "upstream_error",
                "status_code": resp.status_code,
                "body": _safe_body(resp)
            }
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
            "goals": {"home": m["goals"]["home"], "away": m["goals"]["away"]}
        }
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}
