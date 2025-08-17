import os
import requests
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"status": "Backend çalışıyor 🚀"}


@app.get("/live-matches")
def live_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
