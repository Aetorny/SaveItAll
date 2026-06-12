import json
import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from database import get_db, load_tags, save_tags
from models import MediaItemDB
from schemas import MediaItem, MediaItemCreate, MediaItemBase

router = APIRouter(prefix="/api", tags=["API"])
tags = load_tags()

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
        comment=item.comment,
        tags=item.tags
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
    db_item.tags = item.tags

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

@router.get("/add-tag/{item_id}")
def add_tag(item_id: int, tag: str, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    db_item.tags.append(tag) if db_item.tags is not None and tag not in db_item.tags else None
    print(db_item.tags)

    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/remove-tag/{item_id}")
def remove_tag(item_id: int, tag: str, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    if tag in db_item.tags:
        db_item.tags.remove(tag)

    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/tags", response_model=List[str])
def get_tags() -> List[str]:
    return list(tags)

@router.post("/create-tag")
def create_tag(tag: str):
    if tag not in tags:
        tags.add(tag)
        save_tags(tags)
    return {"message": "Тег добавлен"}

@router.post("/delete-tag")
def delete_tag(tag: str, db: Session = Depends(get_db)):
    if tag in tags:
        tags.remove(tag)
        save_tags(tags)
    for item in db.query(MediaItemDB).all():
        if item.tags and tag in item.tags:
            item.tags.remove(tag)
    db.commit()
    return {"message": "Тег удален"}

@router.post("/clear-db")
def clear_db(db: Session = Depends(get_db)):
    db.query(MediaItemDB).delete()
    db.commit()
    return {"message": "База данных очищена"}

@router.get("/export-db")
def export_db(db: Session = Depends(get_db)):
    items = db.query(MediaItemDB).all()
    export_data: list[dict[str, Any]] = []
    for item in items:
        export_data.append({
            "title": item.title,
            "category": item.category,
            "source_url": item.source_url,
            "cover_url": item.cover_url,
            "description": item.description,
            "rating": item.rating,
            "comment": item.comment,
            "tags": item.tags
        })
    
    json_str = json.dumps(export_data, indent=4, ensure_ascii=False)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=saveitall_backup.json"}
    )

@router.post("/import-db")
async def import_db(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    import_data = json.loads(content)
    
    for item in import_data:
        db_item = MediaItemDB(
            title=item.get("title", ""),
            category=item.get("category", ""),
            source_url=item.get("source_url", ""),
            cover_url=item.get("cover_url", ""),
            description=item.get("description", ""),
            rating=item.get("rating"),
            comment=item.get("comment"),
            tags=item.get("tags", [])
        )
        db.add(db_item)
    db.commit()
    return {"message": "Данные успешно импортированы"}
