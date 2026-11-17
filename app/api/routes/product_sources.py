from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Product, ProductSource
from app.schemas.product_source import (
    ProductSourceCreate,
    ProductSourceResponse,
)

router = APIRouter(
    prefix="/api/product-sources",
    tags=["Product Sources"],
)


@router.post("/", response_model=ProductSourceResponse, status_code=201)
def create_product_source(
    payload: ProductSourceCreate,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == payload.product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    source = ProductSource(
        product_id=payload.product_id,
        field_name=payload.field_name,
        source_url=str(payload.source_url),
        source_title=payload.source_title,
        source_type=payload.source_type,
        evidence_excerpt=payload.evidence_excerpt,
        verification_status="pending",
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@router.get(
    "/product/{product_id}",
    response_model=List[ProductSourceResponse],
)
def get_product_sources(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return (
        db.query(ProductSource)
        .filter(ProductSource.product_id == product_id)
        .order_by(ProductSource.retrieved_at.desc())
        .all()
    )


@router.get("/", response_model=List[ProductSourceResponse])
def list_product_sources(
    verification_status: str = Query(
        "pending",
        pattern="^(pending|verified|rejected)$",
    ),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(ProductSource)
        .filter(
            ProductSource.verification_status == verification_status
        )
        .order_by(ProductSource.retrieved_at.desc())
        .limit(limit)
        .all()
    )


from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Literal


class ProductSourceReview(BaseModel):
    verification_status: Literal["verified", "rejected"]
    review_notes: str = Field(min_length=10, max_length=2000)


@router.patch("/{source_id}/review", response_model=ProductSourceResponse)
def review_product_source(
    source_id: int,
    payload: ProductSourceReview,
    db: Session = Depends(get_db),
):
    source = db.query(ProductSource).filter(
        ProductSource.id == source_id
    ).first()

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Product source not found",
        )

    source.verification_status = payload.verification_status
    source.review_notes = payload.review_notes
    source.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(source)

    return source
