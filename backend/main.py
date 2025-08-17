from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "v3.football.api-sports.io"
BASE_URL = f"https://{API_HOST}"

headers = {
    "x-apisports-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}

# --- Yorum Üretici ---
def yorum_uret(stats):
    yorumlar = []
    possession = stats.get("Ball Possession", "0%")
    shots = stats.get("Shots on Goal", 0)
    corners = stats.get("Corner Kicks", 0)
    danger = stats.get("Dangerous Attacks", 0)

    try:
        possession_val = int(possession.replace("%", ""))
    except:
        possession_val = 0

    if possession_val > 60:
        yorumlar.append("Topa daha çok sahip olan taraf, oyunu kontrol ediyor.")

    if shots >= 5:
        yorumlar.append("Çok sayıda isabetli şut ile gol arıyor.")

    if corners >= 5:
        yorumlar.append("Sık sık korner kullanıyor, baskılı oynuyor.")

    if danger >= 30:
        yorumlar.append("Gol atmaya çok yakın, sürekli atak yapıyor.")

    if not yorumlar:
        yorumlar.append("Maç dengeli gidiyor, öne çıkan istatistik yok.")

    return yorumlar


# --- Canlı maç arama ---
@app.get("/search-match")
def search_match(team: str = Query(..., min_length=2)):
    fixtures_url = f"{BASE_URL}/fixtures"
    params = {"live": "all"}
    resp = requests.get(fixtures_url, headers=headers, params=params)
    
    if resp.status_code != 200:
        return {"error": f"API isteği başarısız oldu: {resp.status_code}"}

    data = resp.json()
    for match in data.get("response", []):
        home = match["teams"]["home"]["name"].lower()
        away = match["teams"]["away"]["name"].lower()

        if team.lower() in home or team.lower() in away:
            fixture_id = match["fixture"]["id"]

            # İstatistikleri çek
            stats_url = f"{BASE_URL}/fixtures/statistics"
            stats_resp = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
            stats_data = stats_resp.json()

            stats_map = {}
            if stats_resp.status_code == 200 and stats_data.get("response"):
                for stat in stats_data["response"]:
                    if stat["team"]["id"] == match["teams"]["home"]["id"]:  # sadece home takım istatistikleri alındı
                        for s in stat["statistics"]:
                            stats_map[s["type"]] = s["value"] if s["value"] is not None else 0

            yorumlar = yorum_uret(stats_map)

            return {
                "match": {
                    "home": match["teams"]["home"]["name"],
                    "away": match["teams"]["away"]["name"],
                    "score": f"{match['goals']['home']} - {match['goals']['away']}",
                    "league": match["league"]["name"],
                    "country": match["league"]["country"],
                    "minute": match["fixture"]["status"]["elapsed"],
                    "status": match["fixture"]["status"]["long"],
                    "fixture_id": fixture_id,
                },
                "yorumlar": yorumlar,
            }

    return {"message": "Maç bulunamadı."}
