from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine
import os
import sys
import json
from settings import IS_EXE

SQLALCHEMY_DATABASE_URL = "sqlite:///./media.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

def auto_migrate_database(engine: Engine):
    """
    Безопасно добавляет колонку created_date, если её еще нет в базе у пользователя.
    """
    with engine.connect() as conn:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        columns = [col['name'] for col in inspector.get_columns('media_items')]
        
        if 'created_date' not in columns:
            print("Обнаружена старая версия БД. Добавляем колонку created_date...")
            conn.execute(text("ALTER TABLE media_items ADD COLUMN created_date VARCHAR;"))
            conn.commit()
            print("База данных успешно обновлена до новой версии!")
        else:
            print("База данных уже актуальной версии.")

auto_migrate_database(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if IS_EXE:
    BACKEND_FOLDER = os.path.dirname(sys.executable)
else:
    BACKEND_FOLDER = os.path.dirname(os.path.abspath(__file__)) # type: ignore

if not os.path.exists(os.path.join(BACKEND_FOLDER, 'tags.json')):
    with open(os.path.join(BACKEND_FOLDER, 'tags.json'), 'w') as f:
        f.write('[]')

def load_tags() -> set[str]:
    with open(os.path.join(BACKEND_FOLDER, 'tags.json'), 'r') as f:
        return set(json.load(f))

def save_tags(tags: set[str]):
    with open(os.path.join(BACKEND_FOLDER, 'tags.json'), 'w') as f:
        json.dump(list(tags), f, indent=4, ensure_ascii=False)
