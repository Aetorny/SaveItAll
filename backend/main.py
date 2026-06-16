import os
import pathlib
import sys
import atexit
import threading

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from settings import settings, IS_EXE, get_resource_path
from api import router as api_router
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

app = FastAPI(title="Save It All API")

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
    host=settings.BACKEND_IP,
    port=settings.BACKEND_PORT,
)

server = uvicorn.Server(config)

def run_api():
    server.run()

if __name__ == "__main__":
    atexit.register(stop_frontend)

    build_dir = find_frontend_build()
    if IS_EXE:
        build_dir_for_exe = get_resource_path("dist")
        app.mount('/', StaticFiles(directory=str(build_dir_for_exe), html=True), name='frontend_static')
        @app.exception_handler(404)
        async def not_found_handler(request, exc): # type: ignore
            return FileResponse(os.path.join(build_dir_for_exe, "index.html"))
    else:
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
            "Save It All",
            f"{settings.BACKEND_IP}:{5173 if settings.IS_RUN_DEV and not IS_EXE else settings.BACKEND_PORT}",
            maximized=True,
            focus=True,
        )
        user_data_dir = os.path.join(pathlib.Path.home(), ".save_it_all_data")
        webview.start(
            private_mode=False,
            storage_path=user_data_dir,
            debug=True
        )
    finally:
        server.should_exit = True
        stop_frontend()
        os._exit(0)
