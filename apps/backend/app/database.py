import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

# Existing process environment variables have highest priority. A
# backend-specific .env takes precedence over the shared root .env.
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(REPOSITORY_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
	raise RuntimeError(
		"DATABASE_URL is required. Copy .env.example to .env and set your local "
		"PostgreSQL connection string there."
	)

engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("postgresql"):
	engine_kwargs["connect_args"] = {"connect_timeout": 5}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
	pass


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
