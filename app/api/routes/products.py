from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.services.product_repo import ProductRepository
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    keyword: Optional[str] = Query(None, description="Search term in name, description, or ingredients"),
    skin_type: Optional[str] = Query(None, description="Target skin type e.g., Sensitive, Dry, Oily"),
    category: Optional[str] = Query(None, description="Category name e.g., Sunscreen, Skincare"),
    brand: Optional[str] = Query(None, description="Brand name e.g., CeraVe, La Roche-Posay"),
    min_spf: Optional[int] = Query(None, description="Minimum SPF level"),
    limit: int = Query(5, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    """
    اندپوینت ساختاریافته جستجوی محصولات آرایشی و بهداشتی.
    """
    products = ProductRepository.search_products(
        db=db,
        keyword=keyword,
        skin_type=skin_type,
        category_name=category,
        brand_name=brand,
        min_spf=min_spf,
        limit=limit
    )
    return products
