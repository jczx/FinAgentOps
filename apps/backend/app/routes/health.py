from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
	try:
		with SessionLocal() as db:
			db.execute(text("SELECT 1"))
		database_status = "reachable"
		status = "ok"
	except SQLAlchemyError:
		database_status = "unreachable"
		status = "degraded"

	return HealthResponse(
		status=status,
		service="finagentops-api",
		database=database_status,
	)
