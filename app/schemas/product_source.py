from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProductSourceCreate(BaseModel):
    product_id: int = Field(gt=0)
    field_name: str = Field(min_length=1, max_length=100)
    source_url: HttpUrl
    source_title: Optional[str] = Field(default=None, max_length=300)
    source_type: Optional[str] = Field(default=None, max_length=100)
    evidence_excerpt: Optional[str] = None


class ProductSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    field_name: str
    source_url: str
    source_title: Optional[str]
    source_type: Optional[str]
    evidence_excerpt: Optional[str]
    retrieved_at: datetime
    verification_status: str
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
