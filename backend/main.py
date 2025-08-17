from fastapi import FastAPI
import requests
import os

app = FastAPI()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "v3.football.api-sports.io"

@app.get("/")
def home():
    return {"status": "Backend çalışıyor"}

@app.get("/match-stats/{fixture_id}")
def match_stats(fixture_id: int):
    url = f"https://{API_HOST}/fixtures?id={fixture_id}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"API isteği başarısız oldu: {response.status_code}"}

    data = response.json()

    if not data.get("response"):
        return {"message": "Bu ID için maç bulunamadı"}

    match = data["response"][0]
    return {
        "fixture_id": match["fixture"]["id"],
        "date": match["fixture"]["date"],
        "status": match["fixture"]["status"]["long"],
        "league": match["league"]["name"],
        "country": match["league"]["country"],
        "home_team": match["teams"]["home"]["name"],
        "away_team": match["teams"]["away"]["name"],
        "goals": {
            "home": match["goals"]["home"],
            "away": match["goals"]["away"]
        }
    }
