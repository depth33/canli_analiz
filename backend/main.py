from fastapi import FastAPI
import requests
import os

app = FastAPI()

API_URL = "https://free-football-soccer-videos.p.rapidapi.com/"
API_HOST = "free-football-soccer-videos.p.rapidapi.com"
API_KEY = os.getenv("RAPIDAPI_KEY", "5c917a0525msh5efba96e0642f5ap107857jsnaefe35397696")


@app.get("/")
def home():
    return {"status": "Backend çalışıyor 🚀"}


@app.get("/live-matches")
def get_live_matches():
    url = "https://free-football-soccer-videos.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}
