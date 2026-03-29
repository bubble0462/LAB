from __future__ import annotations

from decimal import Decimal
from math import ceil

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models import InvoiceRecord


def list_invoices(
    session: Session,
    *,
    search_keyword: str = "",
    invoice_status: str | None = None,
    ownership_type: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    page = max(page, 1)
    page_size = max(page_size, 1)

    conditions = []
    keyword = search_keyword.strip()
    if keyword:
        pattern = f"%{keyword}%"
        conditions.append(
            or_(
                InvoiceRecord.product_name.ilike(pattern),
                InvoiceRecord.model.ilike(pattern),
                InvoiceRecord.owner_name.ilike(pattern),
                InvoiceRecord.remarks.ilike(pattern),
            )
        )

    if invoice_status:
        conditions.append(InvoiceRecord.invoice_status == invoice_status)

    if ownership_type:
        conditions.append(InvoiceRecord.ownership_type == ownership_type)

    base_query = select(InvoiceRecord)
    count_query = select(func.count(InvoiceRecord.id)).select_from(InvoiceRecord)
    summary_query = select(
        func.count(InvoiceRecord.id),
        func.coalesce(func.sum(InvoiceRecord.quantity), 0),
        func.coalesce(func.sum(InvoiceRecord.total_amount), Decimal("0.00")),
        func.coalesce(
            func.sum(
                case((InvoiceRecord.invoice_status == "待开", 1), else_=0),
            ),
            0,
        ),
    ).select_from(InvoiceRecord)

    if conditions:
        base_query = base_query.where(*conditions)
        count_query = count_query.where(*conditions)
        summary_query = summary_query.where(*conditions)

    total = session.scalar(count_query) or 0
    total_pages = max(ceil(total / page_size), 1) if total else 1
    current_page = min(page, total_pages)

    rows = session.execute(summary_query).one()
    total_records, total_quantity, total_amount, pending_count = rows

    invoices = session.scalars(
        base_query.order_by(InvoiceRecord.purchase_date.desc(), InvoiceRecord.id.desc())
        .offset((current_page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": invoices,
        "page": current_page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "summary": {
            "records": total_records or 0,
            "quantity": total_quantity or 0,
            "amount": total_amount or Decimal("0.00"),
            "pending_count": pending_count or 0,
        },
    }
def get_invoice(session: Session, invoice_id: int) -> InvoiceRecord | None:
    return session.get(InvoiceRecord, invoice_id)


def create_invoice(session: Session, invoice_data: dict) -> InvoiceRecord:
    invoice = InvoiceRecord(**invoice_data)
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


def update_invoice(session: Session, invoice: InvoiceRecord, invoice_data: dict) -> InvoiceRecord:
    for field_name, value in invoice_data.items():
        setattr(invoice, field_name, value)

    session.commit()
    session.refresh(invoice)
    return invoice


def delete_invoice(session: Session, invoice: InvoiceRecord) -> None:
    session.delete(invoice)
    session.commit()
