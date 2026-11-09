from backend.shared.config import settings
from backend.shared.database import create_database


engine, SessionLocal, Base = create_database(
    settings.orchestrator_database
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()