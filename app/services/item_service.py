from __future__ import annotations

from math import ceil

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Category, Item


def list_items(
    session: Session,
    *,
    search_keyword: str = "",
    category_id: int | None = None,
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
                Item.name.ilike(pattern),
                Item.model.ilike(pattern),
                Category.name.ilike(pattern),
                Item.function_description.ilike(pattern),
            )
        )

    if category_id is not None:
        conditions.append(Item.category_id == category_id)

    base_query = select(Item).join(Category).options(joinedload(Item.category))
    count_query = select(func.count(Item.id)).select_from(Item).join(Category)

    if conditions:
        base_query = base_query.where(*conditions)
        count_query = count_query.where(*conditions)

    total = session.scalar(count_query) or 0
    total_pages = max(ceil(total / page_size), 1) if total else 1
    current_page = min(page, total_pages)

    items = session.scalars(
        base_query.order_by(Item.updated_at.desc(), Item.id.desc())
        .offset((current_page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": items,
        "page": current_page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


def get_item(session: Session, item_id: int) -> Item | None:
    statement = select(Item).options(joinedload(Item.category)).where(Item.id == item_id)
    return session.scalar(statement)


def create_item(session: Session, item_data: dict) -> Item:
    item = Item(**item_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update_item(session: Session, item: Item, item_data: dict) -> Item:
    for field_name, value in item_data.items():
        setattr(item, field_name, value)

    session.commit()
    session.refresh(item)
    return item


def delete_item(session: Session, item: Item) -> None:
    session.delete(item)
    session.commit()

