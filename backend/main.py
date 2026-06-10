from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
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
import threading
import webbrowser
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

def _find_frontend_build() -> Path | None:
        candidates = [FRONTEND_DIR / 'dist', FRONTEND_DIR / 'build', FRONTEND_DIR / 'output']
        for d in candidates:
                if d.exists() and d.is_dir():
                        return d
        return None


def _is_dev_server_up() -> bool:
    try:
        req = urllib.request.Request('http://127.0.0.1:5173', headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=1) as resp:
            return resp.status < 400
    except Exception:
        return False


@app.get("/__frontend_ready")
def frontend_ready():
    if _find_frontend_build():
        return PlainTextResponse("ready", status_code=200)
    if _is_dev_server_up():
        return PlainTextResponse("ready", status_code=200)
    return PlainTextResponse("not-ready", status_code=503)


@app.get("/")
def serve_frontend_index():
        build_dir = _find_frontend_build()
        if build_dir:
                index = build_dir / 'index.html'
                if index.exists():
                        return FileResponse(index, media_type='text/html')
        if _is_dev_server_up():
            return RedirectResponse('http://127.0.0.1:5173')
        html = """
                <!doctype html>
                <html lang="ru">
                    <head>
                        <meta charset="utf-8" />
                        <meta name="viewport" content="width=device-width, initial-scale=1" />
                        <title>Загрузка…</title>
                        <style>
                            :root{--bg:#0b1220;--card:#0f1724;--muted:#94a3b8;--accent:#60a5fa}
                            html,body{height:100%;margin:0}
                            body{background:radial-gradient(1200px 600px at 10% 20%, rgba(96,165,250,0.06), transparent), var(--bg);color:var(--muted);font-family:Inter,ui-sans-serif,system-ui,Segoe UI,Helvetica,Arial,sans-serif;display:flex;align-items:center;justify-content:center}
                            .box{background:linear-gradient(180deg, rgba(255,255,255,0.02), transparent);padding:28px;border-radius:12px;box-shadow:0 6px 24px rgba(2,6,23,0.6);text-align:center;min-width:320px}
                            h1{color:#e6eef8;margin:0 0 8px 0;font-size:20px}
                            p{margin:0 0 14px 0;color:var(--muted)}
                            .spinner{width:72px;height:72px;border-radius:50%;border:8px solid rgba(255,255,255,0.06);border-top-color:var(--accent);animation:spin 1s linear infinite;margin:0 auto 16px}
                            .dots{display:flex;gap:8px;justify-content:center}
                            .dot{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,0.08);animation:pulse 1.2s infinite}
                            .dot:nth-child(1){animation-delay:0s}
                            .dot:nth-child(2){animation-delay:0.15s}
                            .dot:nth-child(3){animation-delay:0.3s}
                            @keyframes spin{to{transform:rotate(360deg)}}
                            @keyframes pulse{0%{transform:translateY(0);opacity:0.6}50%{transform:translateY(-6px);opacity:1}100%{transform:translateY(0);opacity:0.6}}
                            small{display:block;margin-top:8px;color:#7e8aa3;font-size:12px}
                        </style>
                    </head>
                    <body>
                        <div class="box">
                            <div class="spinner" aria-hidden></div>
                            <h1>Загрузка фронтенда…</h1>
                            <p>Страницу можно открыть через порт <strong>5173</strong> при запущенном dev‑сервере.</p>
                            <div class="dots" aria-hidden>
                                <div class="dot"></div>
                                <div class="dot"></div>
                                <div class="dot"></div>
                            </div>
                            <small>Авто‑обновление выполняется каждые 1.5 секунды.</small>
                        </div>
                        <script>
                            async function check(){
                                try{
                                    const r = await fetch('/__frontend_ready');
                                    if(r.ok){ location.reload(); return; }
                                }catch(e){}
                                setTimeout(check,1500);
                            }
                            check();
                        </script>
                    </body>
                </html>
                """
        return HTMLResponse(html)

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

    build_dir = _find_frontend_build()
    if build_dir:
        print(f"Найдена сборка фронтенда в {build_dir}, монтирую статические файлы.")
        app.mount('/', StaticFiles(directory=str(build_dir), html=True), name='frontend')

    try:
        frontend_process = start_frontend()
    except FileNotFoundError:
        print("npm не найден. Установите Node.js и npm, чтобы запустить фронтенд.", file=sys.stderr)

    try:
        import uvicorn

        def open_browser():
            try:
                webbrowser.open('http://127.0.0.1:8000')
            except Exception:
                pass

        threading.Timer(1.5, open_browser).start()
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        pass
    finally:
        stop_frontend()
