from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="brand")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    in_stock = Column(Boolean, default=True)
    data_source = Column(String(100), nullable=True)
    verification_status = Column(String(30), default="unverified")

    skin_type = Column(String(100), nullable=True)
    spf = Column(Integer, nullable=True)
    ingredients = Column(Text, nullable=True)
    volume_ml = Column(String(50), nullable=True)
    key_features = Column(Text, nullable=True)

    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
