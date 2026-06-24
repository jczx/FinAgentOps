from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import PipelineRunRecord
from app.models import PipelineStatusResponse

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/status", response_model=PipelineStatusResponse)
def get_pipeline_status(db: Session = Depends(get_db)) -> PipelineStatusResponse:
	try:
		pipeline_run = db.scalar(
			select(PipelineRunRecord).order_by(desc(PipelineRunRecord.last_run_at)),
		)
	except SQLAlchemyError as error:
		raise HTTPException(
			status_code=503,
			detail=(
				"Database is not reachable. Check that PostgreSQL is running, verify "
				"network access, and confirm DATABASE_URL."
			),
		) from error

	if pipeline_run is None:
		raise HTTPException(status_code=404, detail="No pipeline run was found.")

	return PipelineStatusResponse(
		status=pipeline_run.status,
		last_run=pipeline_run.last_run_at.isoformat(),
		steps_completed=pipeline_run.steps_completed,
		total_steps=pipeline_run.total_steps,
		message=pipeline_run.message,
	)
