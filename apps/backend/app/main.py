from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app import db_models
from app.database import SessionLocal, engine
from app.routes import companies, health, pipeline
from app.seed_data import seed_database
from app.services.sec_ingestion import ensure_ingestion_schema

app = FastAPI(
	title="FinAgentOps API",
	description="Backend API for the FinAgentOps financial dashboard.",
	version="0.1.0",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:5173",
		"http://127.0.0.1:5173",
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(companies.router)
app.include_router(pipeline.router)


@app.on_event("startup")
def initialize_database() -> None:
	try:
		ensure_ingestion_schema(engine)
		with SessionLocal() as db:
			seed_database(db)
		app.state.database_startup_error = None
	except SQLAlchemyError as error:
		app.state.database_startup_error = str(error)
