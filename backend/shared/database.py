from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.shared.config import settings


def create_database(database_name: str):
    database_url = (
        f"mysql+pymysql://{settings.mysql_user}:"
        f"{settings.mysql_password}@"
        f"{settings.mysql_host}:"
        f"{settings.mysql_port}/"
        f"{database_name}"
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base = declarative_base()

    return engine, SessionLocal, Base


def get_database_session(SessionLocal):
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()