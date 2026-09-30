"""
SQLite 資料庫連線與 Session 管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# SQLite 多執行緒支援與 check_same_thread=False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI 相依注入 (Dependency Injection) 取得 DB Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
