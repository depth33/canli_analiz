from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "backend çalışıyor"}

@app.get("/live-matches")
def get_live_matches():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    url = "https://api.sofascore.com/api/v1/sport/football/events/live"

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            return {"error": res.status_code, "text": res.text}

        return res.json()

    except Exception as e:
        return {"error": "Exception", "message": str(e)}
