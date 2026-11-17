from pydantic import BaseModel
from typing import Optional

class BrandResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    in_stock: bool = True
    skin_type: Optional[str] = None
    spf: Optional[int] = None
    ingredients: Optional[str] = None
    volume_ml: Optional[str] = None
    key_features: Optional[str] = None
    data_source: Optional[str] = None
    verification_status: Optional[str] = "unverified"

    brand: Optional[BrandResponse] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True
