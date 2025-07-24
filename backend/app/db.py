import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()  # loads .env into environment

# —————————————————————————————
# 1) Connection URL & engine
# —————————————————————————————
DATABASE_URL = (
    f"postgresql+pg8000://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
 )

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
)

def get_engine():
    """
    Returns the SQLAlchemy Engine.
    """
    return engine


# —————————————————————————————
# 2) Session factory & dependency
# —————————————————————————————
# sessionmaker returns a class you can call to get sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

def get_db():
    """
    FastAPI dependency that yields a Session, and
    ensures it’s closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
