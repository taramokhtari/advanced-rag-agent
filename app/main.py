from fastapi import FastAPI
from app.api.routes import products

app = FastAPI(
    title="AI-Powered Beauty Shopping Assistant API",
    version="1.0.0",
    description="Backend API for AI Beauty Assistant using FastAPI, PostgreSQL, and ChromaDB."
)

# ثبت روترها
app.include_router(products.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AI Beauty Shopping Assistant API!",
        "status": "active"
    }
