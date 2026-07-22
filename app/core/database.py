from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# The engine is the core connection to the database.
engine = create_engine(settings.database_url, echo=settings.debug)

# A session factory: each request will use its own session for database work.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The base class that all our ORM models will inherit from.
Base = declarative_base()


def get_db():
    """Provide a database session for a request, and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()