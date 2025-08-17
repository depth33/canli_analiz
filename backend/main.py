from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://canli-analiz.vercel.app"],  # sadece senin frontend domainin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Backend çalışıyor 🚀"}

@app.get("/test")
def test_api():
    return {"message": "Frontend ve Backend bağlantısı başarılı ✅"}
