from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}


@app.get("/")
def root():
    return {"status": "Backend çalışıyor"}


@app.get("/match-by-team")
def match_by_team(team: str = Query(..., description="Takım adı")):
    """
    Kullanıcıdan takım adı alır, canlı maçlar içinden filtreleyip geri döner
    """
    try:
        url = f"{BASE_URL}?live=all"
        res = requests.get(url, headers=headers)
        data = res.json()

        if "response" not in data or len(data["response"]) == 0:
            return {"message": "Şu anda canlı maç bulunmuyor."}

        # Takım adına göre filtrele
        filtered = []
        for match in data["response"]:
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            if team.lower() in home.lower() or team.lower() in away.lower():
                filtered.append({
                    "league": match["league"]["name"],
                    "home": home,
                    "away": away,
                    "score": f'{match["goals"]["home"]} - {match["goals"]["away"]}',
                    "minute": match["fixture"]["status"]["elapsed"],
                    "status": match["fixture"]["status"]["long"]
                })

        if not filtered:
            return {"message": f"{team} takımının şu anda canlı maçı yok."}

        return {"results": filtered}

    except Exception as e:
        return {"error": str(e)}
