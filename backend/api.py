import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from database import get_db
from models import MediaItemDB
from schemas import MediaItem, MediaItemCreate, MediaItemBase

router = APIRouter(prefix="/api", tags=["API"])

def process_cover_url(cover: str | None) -> str:
    if not cover:
        return ''
    return cover.strip()

@router.get("/items/{category}", response_model=List[MediaItem])
def get_items(category: str, db: Session = Depends(get_db)):
    return db.query(MediaItemDB).filter(MediaItemDB.category == category).all()

@router.post("/items/", response_model=MediaItem)
def create_item(item: MediaItemCreate, db: Session = Depends(get_db)):
    if item.is_import and not item.source_url:
        raise HTTPException(status_code=400, detail="Для импорта необходима ссылка (source_url)")
    if not item.is_import and not item.title:
        raise HTTPException(status_code=400, detail="Необходимо указать название (title)")

    cover = process_cover_url(item.cover_url)

    db_item = MediaItemDB(
        category=item.category,
        title=item.title,
        source_url=item.source_url,
        cover_url=cover,
        description=item.description,
        rating=item.rating,
        comment=item.comment
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    db.delete(db_item)
    db.commit()
    return {"message": "Элемент удален"}

@router.put("/items/{item_id}", response_model=MediaItem)
def update_item(item_id: int, item: MediaItemBase, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    db_item.category = item.category
    db_item.title = item.title
    db_item.source_url = item.source_url
    db_item.cover_url = process_cover_url(item.cover_url)
    db_item.description = item.description
    db_item.rating = item.rating
    db_item.comment = item.comment

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/fetch-url", response_class=PlainTextResponse)
def fetch_url(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL обязателен")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Неверная схема URL")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read()
            return content.decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise HTTPException(status_code=exc.code if 400 <= exc.code < 600 else 502, detail=str(exc))
    except URLError as exc:
        raise HTTPException(status_code=502, detail=str(exc.reason))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки URL: {exc}")