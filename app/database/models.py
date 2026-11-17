from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    func,
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


class ProductSource(Base):
    __tablename__ = "product_sources"

    __table_args__ = (
        CheckConstraint(
            "verification_status IN ('pending', 'verified', 'rejected')",
            name="check_product_source_verification_status",
        ),
        Index("ix_product_sources_product_field", "product_id", "field_name"),
    )

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    field_name = Column(String(100), nullable=False)
    source_url = Column(Text, nullable=False)
    source_title = Column(String(300), nullable=True)
    source_type = Column(String(100), nullable=True)
    evidence_excerpt = Column(Text, nullable=True)

    retrieved_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    verification_status = Column(
        String(30),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    title = Column(String(250), nullable=True)

    status = Column(
        String(30),
        nullable=False,
        default="active",
        server_default="active",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(
        String(20),
        nullable=False,
    )

    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )
