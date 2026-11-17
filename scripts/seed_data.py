import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.connection import SessionLocal
from app.database.models import Brand, Category, Product


def seed_database():
    db = SessionLocal()

    try:
        brands = [
            Brand(name="CeraVe", description="Skincare brand"),
            Brand(name="The Ordinary", description="Skincare brand"),
            Brand(name="Maybelline", description="Makeup brand"),
        ]

        categories = [
            Category(name="Skincare", description="Skin care products"),
            Category(name="Makeup", description="Makeup products"),
            Category(name="Haircare", description="Hair care products"),
        ]

        for brand in brands:
            if not db.query(Brand).filter_by(name=brand.name).first():
                db.add(brand)

        for category in categories:
            if not db.query(Category).filter_by(name=category.name).first():
                db.add(category)

        db.flush()

        products = [
            {
                "name": "Hydrating Cleanser",
                "description": "A gentle facial cleanser.",
                "price": 15.99,
                "brand": "CeraVe",
                "category": "Skincare",
            },
            {
                "name": "Niacinamide 10% + Zinc 1%",
                "description": "A niacinamide-based skincare serum.",
                "price": 9.50,
                "brand": "The Ordinary",
                "category": "Skincare",
            },
            {
                "name": "Fit Me Foundation",
                "description": "Liquid foundation for makeup.",
                "price": 11.99,
                "brand": "Maybelline",
                "category": "Makeup",
            },
        ]

        for item in products:
            existing = db.query(Product).filter_by(
                name=item["name"]
            ).first()

            if not existing:
                brand = db.query(Brand).filter_by(
                    name=item["brand"]
                ).first()

                category = db.query(Category).filter_by(
                    name=item["category"]
                ).first()

                db.add(Product(
                    name=item["name"],
                    description=item["description"],
                    price=item["price"],
                    brand_id=brand.id,
                    category_id=category.id,
                ))

        db.commit()
        print("Sample data inserted successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
