from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import PipelineRunRecord
from app.models import PipelineRun, PipelineStatusResponse

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/status", response_model=PipelineStatusResponse)
def get_pipeline_status(db: Session = Depends(get_db)) -> PipelineStatusResponse:
	try:
		pipeline_runs = db.scalars(
			select(PipelineRunRecord)
			.order_by(desc(PipelineRunRecord.last_run_at))
			.limit(10),
		).all()
	except SQLAlchemyError as error:
		raise HTTPException(
			status_code=503,
			detail=(
				"Database is not reachable. Check that PostgreSQL is running, verify "
				"network access, and confirm DATABASE_URL."
			),
		) from error

	if not pipeline_runs:
		raise HTTPException(status_code=404, detail="No pipeline run was found.")

	pipeline_run = pipeline_runs[0]

	return PipelineStatusResponse(
		status=pipeline_run.status,
		last_run=pipeline_run.last_run_at.isoformat(),
		steps_completed=pipeline_run.steps_completed,
		total_steps=pipeline_run.total_steps,
		message=pipeline_run.message,
		runs=[
			PipelineRun(
				source_name=row.source_name,
				status=row.status,
				started_at=row.started_at.isoformat() if row.started_at else None,
				finished_at=row.finished_at.isoformat() if row.finished_at else None,
				records_processed=row.records_processed,
				error_message=row.error_message,
				message=row.message,
			)
			for row in pipeline_runs
		],
	)
