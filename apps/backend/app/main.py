from fastapi import FastAPI

from app.routes import companies, health, pipeline

app = FastAPI(
	title="FinAgentOps API",
	description="Mock backend API for the FinAgentOps financial dashboard.",
	version="0.1.0",
)

app.include_router(health.router)
app.include_router(companies.router)
app.include_router(pipeline.router)
