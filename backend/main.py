from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Backend çalışıyor 🚀"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render hangi portu verdiyse onu al
    uvicorn.run(app, host="0.0.0.0", port=port)
