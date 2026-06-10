from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import subprocess
import sys
import atexit
import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError

SQLALCHEMY_DATABASE_URL = "sqlite:///./media.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MediaItemDB(Base):
    __tablename__ = "media_items"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    title = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    cover_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    rating = Column(Integer, default=0)
    comment = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)


class MediaItemBase(BaseModel):
    category: str
    title: Optional[str] = None
    source_url: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[int] = 0
    comment: Optional[str] = None


class MediaItemCreate(MediaItemBase):
    is_import: bool


class MediaItem(MediaItemBase):
    id: int

    class Config:
        from_attributes = True


app = FastAPI(title="Media Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/items/{category}", response_model=List[MediaItem])
def get_items(category: str, db: Session = Depends(get_db)):
    items = db.query(MediaItemDB).filter(MediaItemDB.category == category).all()
    return items

@app.post("/api/items/", response_model=MediaItem)
def create_item(item: MediaItemCreate, db: Session = Depends(get_db)):
    if item.is_import and not item.source_url:
        raise HTTPException(status_code=400, detail="Для импорта необходима ссылка (source_url)")
    if not item.is_import and not item.title:
        raise HTTPException(status_code=400, detail="Необходимо указать название (title)")

    cover = item.cover_url
    if cover:
        cover = cover.strip()
        if cover.startswith('//'):
            cover = 'https:' + cover
        elif cover.startswith('/'):
            try:
                from urllib.parse import urljoin
                base = item.source_url or 'https://shikimori.io'
                cover = urljoin(base, cover)
            except Exception:
                cover = 'https://shikimori.io' + cover

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

@app.get("/api/fetch-url", response_class=PlainTextResponse)
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

@app.get("/")
def read_root():
    return {"message": "Бэкенд Media Tracker успешно работает! Фронтенд ищите на http://localhost:5173"}

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    db.delete(db_item)
    db.commit()
    return {"message": "Элемент удален"}


@app.put("/api/items/{item_id}", response_model=MediaItem)
def update_item(item_id: int, item: MediaItemBase, db: Session = Depends(get_db)):
    db_item = db.query(MediaItemDB).filter(MediaItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    db_item.category = item.category
    db_item.title = item.title
    db_item.source_url = item.source_url
    cover = item.cover_url
    if cover:
        cover = cover.strip()
        if cover.startswith('//'):
            cover = 'https:' + cover
        elif cover.startswith('/'):
            try:
                from urllib.parse import urljoin
                base = item.source_url or 'https://shikimori.io'
                cover = urljoin(base, cover)
            except Exception:
                cover = 'https://shikimori.io' + cover
    db_item.cover_url = cover
    db_item.description = item.description
    db_item.rating = item.rating
    db_item.comment = item.comment

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
frontend_process = None


def start_frontend() -> subprocess.Popen | None:
    npm_command = ["npm.cmd" if sys.platform == "win32" else "npm", "run", "dev", "--", "--host", "127.0.0.1"]
    print(f"Запуск фронтенда из {FRONTEND_DIR}")
    return subprocess.Popen(npm_command, cwd=FRONTEND_DIR)


def stop_frontend() -> None:
    global frontend_process
    if frontend_process is None:
        return
    if frontend_process.poll() is None:
        print("Остановка фронтенда...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()


if __name__ == "__main__":
    atexit.register(stop_frontend)
    try:
        frontend_process = start_frontend()
    except FileNotFoundError:
        print("npm не найден. Установите Node.js и npm, чтобы запустить фронтенд.", file=sys.stderr)
    try:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        pass
    finally:
        stop_frontend()
