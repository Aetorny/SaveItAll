import json
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

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

        if not inspector.has_table("media_items"):
            print("Таблица media_items не существует. Миграция не требуется.")
            return
        
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

APP_NAME = "SaveItAll"

if os.name == "nt":
    data_dir = Path(os.environ["APPDATA"]) / APP_NAME
else:
    data_dir = Path(
        os.environ.get(
            "XDG_DATA_HOME",
            Path.home() / ".local" / "share"
        )
    ) / APP_NAME

data_dir.mkdir(parents=True, exist_ok=True)

TAGS_FILE = data_dir / "tags.json"

if not os.path.exists(TAGS_FILE):
    with open(TAGS_FILE, 'w') as f:
        f.write('[]')

def load_tags() -> set[str]:
    with open(TAGS_FILE, 'r') as f:
        return set(json.load(f))

def save_tags(tags: set[str]):
    with open(TAGS_FILE, 'w') as f:
        json.dump(list(tags), f, indent=4, ensure_ascii=False)
