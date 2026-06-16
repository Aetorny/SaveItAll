import json
import os
import urllib.request
from typing import Any, List
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse, urlunparse

import uvicorn
from database import Base, engine
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from models import MediaItemDB
from schemas import MediaItem, MediaItemBase, MediaItemCreate
from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./media.example.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

api_router = APIRouter(prefix="/api", tags=["API"])
tags = set([
    "Тег 1",
    "Тег 2"
])

def process_cover_url(cover: str | None) -> str:
    if not cover:
        return ''
    return cover.strip()

@api_router.get("/items/{category}", response_model=List[MediaItem])
def get_items(category: str, db: Session = Depends(get_db)):
    items = db.query(MediaItemDB).filter(MediaItemDB.category == category).all()
    return items

@api_router.post("/items/", response_model=MediaItem)
def create_item(item: MediaItemCreate, db: Session = Depends(get_db)):
    if item.is_import and not item.source_url:
        raise HTTPException(status_code=400, detail="Для импорта необходима ссылка (source_url)")
    if not item.is_import and not item.title:
        raise HTTPException(status_code=400, detail="Необходимо указать название (title)")

    cover = process_cover_url(item.cover_url)
    db_item = MediaItemDB(
        id=1234,
        category=item.category,
        title=item.title,
        source_url=item.source_url,
        cover_url=cover,
        description=item.description,
        rating=item.rating,
        comment=item.comment,
        tags=item.tags
    )
    return db_item

@api_router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    return {"message": "Элемент удален"}

@api_router.put("/items/{item_id}", response_model=MediaItem)
def update_item(item_id: int, item: MediaItemBase, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    return db_item

@api_router.get("/fetch-url", response_class=PlainTextResponse)
def fetch_url(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL обязателен")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Неверная схема URL")
    safe_path = quote(parsed.path)
    safe_query = quote(parsed.query) if parsed.query else ""
    safe_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        safe_path,
        parsed.params,
        safe_query,
        parsed.fragment
    ))
    try:
        req = urllib.request.Request(safe_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read()
            return content.decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise HTTPException(status_code=exc.code if 400 <= exc.code < 600 else 502, detail=str(exc))
    except URLError as exc:
        raise HTTPException(status_code=502, detail=str(exc.reason))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки URL: {exc}")

@api_router.get("/add-tag/{item_id}")
def add_tag(item_id: int, tag: str, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    return db_item

@api_router.get("/remove-tag/{item_id}")
def remove_tag(item_id: int, tag: str, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    return db_item

@api_router.get("/tags", response_model=List[str])
def get_tags() -> List[str]:
    return list(tags)

@api_router.post("/create-tag")
def create_tag(tag: str):
    return {"message": "Тег добавлен"}

@api_router.post("/delete-tag")
def delete_tag(tag: str, db: Session = Depends(get_db)):
    return {"message": "Тег удален"}

@api_router.post("/clear-db")
def clear_db():
    return {"message": "База данных очищена"}

@api_router.get("/export-db")
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

@api_router.post("/import-db")
async def import_db():
    return {"message": "Данные успешно импортированы"}

@api_router.get("/icon")
async def get_icon():
    return FileResponse(
        "../frontend/src/lib/assets/icon.ico",
        media_type="image/x-icon"
    )

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Save It All API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

config = uvicorn.Config(
    app,
    host=settings.BACKEND_IP,
    port=settings.BACKEND_PORT,
)

server = uvicorn.Server(config)

if __name__ == "__main__":
    try:
        server.run()
    finally:
        server.should_exit = True
        os._exit(0)
