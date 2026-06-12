from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./media.db"

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

BACKEND_FOLDER = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(BACKEND_FOLDER, 'tags.json')):
    with open(os.path.join(BACKEND_FOLDER, 'tags.json'), 'w') as f:
        f.write('[]')

def load_tags() -> set[str]:
    with open(os.path.join(BACKEND_FOLDER, 'tags.json'), 'r') as f:
        return set(json.load(f))

def save_tags(tags: set[str]):
    with open(os.path.join(BACKEND_FOLDER, 'tags.json'), 'w') as f:
        json.dump(list(tags), f, indent=4, ensure_ascii=False)
