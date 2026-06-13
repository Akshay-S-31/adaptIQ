"""
AdaptIQ AI Engine — Synthesize API Endpoint

POST /internal/ai/synthesize

Receives research queries from the Spring Boot gateway,
launches the research pipeline as a background task,
and returns 200 immediately.
"""

import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import SynthesizeRequest
from app.engine.orchestrator import run_research_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/ai", tags=["internal"])


@router.post("/synthesize")
async def synthesize(
    request: SynthesizeRequest,
    background_tasks: BackgroundTasks,
):
    """
    Accept a research query and launch the autonomous
    ReAct + Reflexion pipeline in the background.

    Returns 200 immediately — results are delivered
    via callback to the Spring Boot gateway.
    """
    logger.info(
        f"Received synthesis request — job_id: {request.job_id}, "
        f"query: '{request.query[:80]}...'"
    )

    # Launch the pipeline as a background task
    background_tasks.add_task(
        run_research_pipeline,
        job_id=request.job_id,
        query=request.query,
    )

    return {
        "status": "accepted",
        "job_id": request.job_id,
        "message": "Research pipeline started",
    }
