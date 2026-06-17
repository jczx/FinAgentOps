from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import companies, health, pipeline

app = FastAPI(
	title="FinAgentOps API",
	description="Mock backend API for the FinAgentOps financial dashboard.",
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
