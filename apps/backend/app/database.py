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

DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql+psycopg2://finagentops_user:finagentops_password@localhost:5432/finagentops",
)

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
	connect_args={"connect_timeout": 5},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
	pass


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
