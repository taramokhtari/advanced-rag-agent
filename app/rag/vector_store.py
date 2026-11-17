import os

import chromadb
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import SessionLocal
from app.database.models import Product


class BGEEmbeddingFunction(chromadb.EmbeddingFunction):

    def __init__(
        self,
        base_url: str = "http://172.21.176.1:11434",
        model: str = "bge-m3",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    @staticmethod
    def name() -> str:
        return "bge_m3_ollama"

    def __call__(
        self,
        input: chromadb.Documents,
    ) -> chromadb.Embeddings:

        response = httpx.post(
            f"{self.base_url}/api/embed",
            json={
                "model": self.model,
                "input": input,
            },
            timeout=120.0,
        )

        response.raise_for_status()

        data = response.json()

        if "embeddings" not in data:
            raise RuntimeError(
                f"Ollama embedding response is invalid: {data}"
            )

        return data["embeddings"]

    def get_config(self) -> dict:
        return {
            "base_url": self.base_url,
            "model": self.model,
        }

    @staticmethod
    def build_from_config(config: dict):
        return BGEEmbeddingFunction(
            base_url=config["base_url"],
            model=config["model"],
        )


class ProductVectorStore:

    def __init__(self):

        self.persist_directory = os.path.abspath("storage/chroma")
        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.persist_directory
        )

        self.embedding_fn = BGEEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name="beauty_products_bge_m3",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest_products(self):

        db: Session = SessionLocal()

        try:
            products = (
                db.query(Product)
                .filter(Product.verification_status == "verified")
                .all()
            )

            if not products:
                print("No products found in PostgreSQL to ingest.")
                return

            documents = []
            metadatas = []
            ids = []

            for product in products:

                brand_name = (
                    product.brand.name
                    if product.brand else "Unknown Brand"
                )

                category_name = (
                    product.category.name
                    if product.category else "General"
                )

                doc_text = (
                    f"Product Name: {product.name}\n"
                    f"Brand: {brand_name}\n"
                    f"Category: {category_name}\n"
                    f"Price: {product.price} {product.currency}\n"
                    f"Skin Type: {product.skin_type or 'All'}\n"
                    f"SPF: {product.spf or 'N/A'}\n"
                    f"Key Ingredients: {product.ingredients or 'N/A'}\n"
                    f"Key Features: {product.key_features or 'N/A'}\n"
                    f"Description: {product.description or ''}"
                )

                documents.append(doc_text)

                metadatas.append({
                    "product_id": product.id,
                    "name": product.name,
                    "brand": brand_name,
                    "category": category_name,
                    "price": float(product.price) if product.price else 0.0,
                })

                ids.append(str(product.id))

            print(
                f"Preparing to embed {len(products)} products "
                "with BGE-M3..."
            )

            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

            print(
                f"Successfully ingested {len(products)} products "
                "into ChromaDB!"
            )

        finally:
            db.close()

    def semantic_search(
        self,
        query: str,
        n_results: int = 3,
    ):

        count = self.collection.count()

        if count == 0:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        results = self.collection.query(
            query_texts=[query],
            n_results=min(max(n_results, 1), count),
        )

        return results
