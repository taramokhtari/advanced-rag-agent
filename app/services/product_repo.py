from sqlalchemy.orm import Session
from app.database.models import Product, Brand, Category

class ProductRepository:
    @staticmethod
    def search_products(
        db: Session,
        keyword: str = None,
        skin_type: str = None,
        category_name: str = None,
        brand_name: str = None,
        min_spf: int = None,
        limit: int = 5
    ):
        """
        جستجوی ساختاریافته محصولات با فیلترهای مشخص برای استفاده در ابزارهای ایجنت.
        """
        query = db.query(Product).filter(
            Product.verification_status == "verified"
        )

        # فیلتر متنی روی نام یا توضیحات یا ترکیبات
        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(
                (Product.name.ilike(search_term)) |
                (Product.description.ilike(search_term)) |
                (Product.ingredients.ilike(search_term))
            )

        # فیلتر نوع پوست (مثلاً Oily یا Dry یا Sensitive)
        if skin_type:
            query = query.filter(Product.skin_type.ilike(f"%{skin_type}%"))

        # فیلتر دسته‌بندی
        if category_name:
            query = query.join(Category).filter(Category.name.ilike(f"%{category_name}%"))

        # فیلتر برند
        if brand_name:
            query = query.join(Brand).filter(Brand.name.ilike(f"%{brand_name}%"))

        # فیلتر حداقل SPF
        if min_spf is not None:
            query = query.filter(Product.spf >= min_spf)

        return query.limit(limit).all()

    @staticmethod
    def get_all_products(db: Session, skip: int = 0, limit: int = 50):
        return (
            db.query(Product)
            .order_by(Product.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_product_by_id(db: Session, product_id: int):
        return db.query(Product).filter(Product.id == product_id).first()
