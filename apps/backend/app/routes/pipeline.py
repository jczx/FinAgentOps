from fastapi import APIRouter

from app.mock_data import MOCK_PIPELINE_STATUS
from app.models import PipelineStatusResponse

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/status", response_model=PipelineStatusResponse)
def get_pipeline_status() -> PipelineStatusResponse:
	return MOCK_PIPELINE_STATUS
