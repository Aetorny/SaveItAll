import os

import uvicorn
from api import router as api_router
from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import settings

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

config = uvicorn.Config(
    app,
    host=settings.BACKEND_IP,
    port=settings.PORT,
)

server = uvicorn.Server(config)


if __name__ == "__main__":
    try:
        server.run()
    finally:
        server.should_exit = True
        os._exit(0)
