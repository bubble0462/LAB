from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    items: Mapped[list["Item"]] = relationship(back_populates="category")


class Item(TimestampMixin, Base):
    __tablename__ = "items"
    __table_args__ = (CheckConstraint("quantity >= 0", name="ck_items_quantity_non_negative"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    key_specifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    function_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    category: Mapped[Category] = relationship(back_populates="items")


class InvoiceRecord(TimestampMixin, Base):
    __tablename__ = "invoice_records"
    __table_args__ = (
        CheckConstraint("quantity >= 1", name="ck_invoice_records_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_invoice_records_unit_price_non_negative"),
        CheckConstraint("total_amount >= 0", name="ck_invoice_records_total_amount_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    invoice_status: Mapped[str] = mapped_column(String(20), nullable=False, default="待开", index=True)
    ownership_type: Mapped[str] = mapped_column(String(20), nullable=False, default="公共", index=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
