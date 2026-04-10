# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Verifica conexiones antes de usarlas
    pool_recycle=300,        # Recicla conexiones cada 5 minutos
    pool_size=2,             # Conexiones base en el pool (Railway free tier: 21 max)
    max_overflow=3,          # Conexiones adicionales bajo carga (total máx: 5 por worker)
    pool_timeout=10,         # Segundos de espera antes de lanzar TimeoutError
    echo=settings.DEBUG      # SQL logging solo en debug mode
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    from app.models.base import Base
    Base.metadata.drop_all(bind=engine)