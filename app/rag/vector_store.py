import os
import chromadb
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import Product

class ProductVectorStore:
    def __init__(self):
        # اتصال به ChromaDB به صورت پایدار روی دیسک
        self.persist_directory = os.path.abspath("storage/chroma")
        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # استفاده از کالکشن (ChromaDB به طور پیش‌فرض از مدل محلی all-MiniLM-L6-v2 استفاده می‌کند)
        self.collection = self.client.get_or_create_collection(name="beauty_products_local")

    def ingest_products(self):
        """خواندن محصولات از PostgreSQL و ایندکس کردن آن‌ها در ChromaDB با امبدینگ محلی"""
        db: Session = SessionLocal()
        try:
            products = db.query(Product).all()
            if not products:
                print("No products found in PostgreSQL to ingest.")
                return

            documents = []
            metadatas = []
            ids = []

            for p in products:
                brand_name = p.brand.name if p.brand else "Unknown Brand"
                category_name = p.category.name if p.category else "General"

                # ساخت متن غنی برای جستجوی معنایی
                doc_text = (
                    f"Product Name: {p.name}\n"
                    f"Brand: {brand_name}\n"
                    f"Category: {category_name}\n"
                    f"Price: {p.price} {p.currency}\n"
                    f"Skin Type: {p.skin_type or 'All'}\n"
                    f"SPF: {p.spf or 'N/A'}\n"
                    f"Key Ingredients: {p.ingredients or 'N/A'}\n"
                    f"Key Features: {p.key_features or 'N/A'}\n"
                    f"Description: {p.description or ''}"
                )

                documents.append(doc_text)
                metadatas.append({
                    "product_id": p.id,
                    "name": p.name,
                    "brand": brand_name,
                    "category": category_name,
                    "price": float(p.price) if p.price else 0.0
                })
                ids.append(str(p.id))

            # افزودن یا بروزرسانی در ChromaDB (مدل داخلی به طور خودکار امبدینگ را می‌سازد)
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Successfully ingested {len(products)} products into ChromaDB (using local embeddings)!")

        finally:
            db.close()

    def semantic_search(self, query: str, n_results: int = 3):
        """جستجوی معنایی محلی بر اساس پرسجوی طبیعی کاربر"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
