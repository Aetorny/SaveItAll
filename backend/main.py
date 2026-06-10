import sys
import atexit
import threading
import webbrowser

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from api import router as api_router
from frontend_link import (
    router as frontend_router, 
    start_frontend, 
    stop_frontend, 
    find_frontend_build
)
import frontend_link as frontend # Для доступа к frontend.frontend_process

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Media Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(api_router)
app.include_router(frontend_router)

if __name__ == "__main__":
    atexit.register(stop_frontend)

    build_dir = find_frontend_build()
    if build_dir:
        print(f"Найдена сборка фронтенда в {build_dir}, монтирую статические файлы.")
        # Монтируем статику (переопределит маршрут "/", если не найдено - отработает frontend_router)
        app.mount('/', StaticFiles(directory=str(build_dir), html=True), name='frontend_static')

    try:
        frontend.frontend_process = start_frontend() # pyright: ignore[reportAttributeAccessIssue]
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