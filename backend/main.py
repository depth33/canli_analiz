from fastapi import FastAPI, Query
import requests
import os

app = FastAPI()

# RapidAPI bilgilerini ortam değişkenlerinden alıyoruz
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"

@app.get("/")
def home():
    return {"status": "backend çalışıyor"}

# ✅ Tüm canlı maçları getiren endpoint
@app.get("/live-matches")
def get_live_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"live": "all"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        return {"error": f"API isteği başarısız oldu: {response.status_code}"}

    data = response.json()
    matches = []

    for match in data.get("response", []):
        matches.append({
            "fixture": match["fixture"],
            "league": match["league"],
            "teams": match["teams"],
            "goals": match["goals"],
            "score": match["score"]
        })

    if not matches:
        return {"message": "Şu anda canlı maç bulunmuyor."}

    return matches

# ✅ Tek maç istatistiği için endpoint
@app.get("/match-stats")
def get_match_stats(fixture_id: int = Query(..., description="Maç fixture ID'si")):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"id": fixture_id}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        return {"error": f"API isteği başarısız oldu: {response.status_code}"}

    data = response.json()
    if not data.get("response"):
        return {"message": "Bu ID için maç bulunamadı."}

    match = data["response"][0]

    return {
        "fixture": match["fixture"],
        "league": match["league"],
        "teams": match["teams"],
        "goals": match["goals"],
        "score": match["score"]
    }
