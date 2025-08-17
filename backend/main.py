from fastapi import FastAPI

# Uygulama
app = FastAPI()

# Ana test endpoint
@app.get("/")
def home():
    return {"status": "Backend çalışıyor 🚀"}

# İleride canlı maç analizi endpointleri buraya eklenecek
@app.get("/test")
def test():
    return {"msg": "API başarıyla çalışıyor ✅"}
