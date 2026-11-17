from fastapi import FastAPI

from app.api.routes import products, product_sources, chat

app = FastAPI(
    title="AI-Powered Beauty Shopping Assistant API",
    version="1.0.0",
    description=(
        "Persian AI Beauty Shopping Assistant "
        "powered by Ollama, PostgreSQL, and ChromaDB."
    ),
)

app.include_router(products.router)
app.include_router(product_sources.router)
app.include_router(chat.router)


@app.get("/")
def read_root():
    return {
        "message": "دستیار هوشمند فروشگاه زیبایی فعال است.",
        "status": "active",
    }
