from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Item


def list_categories(session: Session) -> list[Category]:
    statement = select(Category).order_by(Category.name.asc(), Category.id.asc())
    return list(session.scalars(statement).all())


def list_categories_with_item_counts(session: Session) -> list[dict]:
    statement = (
        select(Category, func.count(Item.id).label("item_count"))
        .outerjoin(Item, Item.category_id == Category.id)
        .group_by(
            Category.id,
            Category.name,
            Category.description,
            Category.created_at,
            Category.updated_at,
        )
        .order_by(Category.name.asc(), Category.id.asc())
    )

    rows = session.execute(statement).all()
    return [
        {
            "category": category,
            "item_count": item_count,
        }
        for category, item_count in rows
    ]


def get_category(session: Session, category_id: int) -> Category | None:
    return session.get(Category, category_id)


def is_category_name_taken(session: Session, name: str, exclude_category_id: int | None = None) -> bool:
    normalized_name = name.strip().lower()
    statement = select(Category.id).where(func.lower(Category.name) == normalized_name)

    if exclude_category_id is not None:
        statement = statement.where(Category.id != exclude_category_id)

    return session.scalar(statement) is not None


def create_category(session: Session, name: str, description: str | None) -> Category:
    category = Category(name=name.strip(), description=description or None)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def update_category(session: Session, category: Category, name: str, description: str | None) -> Category:
    category.name = name.strip()
    category.description = description or None
    session.commit()
    session.refresh(category)
    return category


def count_items_for_category(session: Session, category_id: int) -> int:
    statement = select(func.count(Item.id)).where(Item.category_id == category_id)
    return session.scalar(statement) or 0


def delete_category(session: Session, category: Category) -> None:
    linked_items = count_items_for_category(session, category.id)
    if linked_items > 0:
        raise ValueError("该分类下仍有器件，不能直接删除。请先修改或删除相关器件。")

    session.delete(category)
    session.commit()
