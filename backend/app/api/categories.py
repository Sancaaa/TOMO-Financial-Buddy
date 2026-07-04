from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(
    prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[CategoryOut])
def list_categories(
    type: str | None = None, db: Session = Depends(get_db)
) -> list[Category]:
    stmt = select(Category).order_by(Category.type, Category.name)
    if type is not None:
        stmt = stmt.where(Category.type == type)
    return list(db.scalars(stmt).all())


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate, db: Session = Depends(get_db)
) -> Category:
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)
) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Kategori tidak ditemukan")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Kategori tidak ditemukan")
    db.delete(category)
    db.commit()
