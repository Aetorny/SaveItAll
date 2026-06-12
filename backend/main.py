import os
import sys
import atexit
import threading

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from api import router as api_router
from settings import settings
from frontend_link import (
    router as frontend_router, 
    start_frontend, 
    stop_frontend, 
    find_frontend_build
)
import frontend_link as frontend
import webview
import uvicorn

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

config = uvicorn.Config(
    app,
    host="127.0.0.1",
    port=settings.BACKEND_PORT,
)

server = uvicorn.Server(config)

def run_api():
    server.run()

if __name__ == "__main__":
    atexit.register(stop_frontend)

    build_dir = find_frontend_build()
    if settings.IS_RUN_DEV or not build_dir:
        try:
            frontend.frontend_process = start_frontend() # pyright: ignore[reportAttributeAccessIssue]
        except FileNotFoundError:
            print("npm не найден. Установите Node.js и npm, чтобы запустить фронтенд.", file=sys.stderr)
    else:
        print(f"Найдена сборка фронтенда в {build_dir}, монтирую статические файлы.")
        app.mount('/', StaticFiles(directory=str(build_dir), html=True), name='frontend_static')

    try:
        api_thread = threading.Thread(
            target=run_api,
            daemon=True
        )
        api_thread.start()
        webview.create_window( # type: ignore
            "Media Tracker",
            f"http://127.0.0.1:{settings.FRONTEND_PORT if settings.IS_RUN_DEV else settings.BACKEND_PORT}",
            maximized=True,
            focus=True,
        )
        webview.start()
    finally:
        server.should_exit = True
        stop_frontend()
        os._exit(0)
