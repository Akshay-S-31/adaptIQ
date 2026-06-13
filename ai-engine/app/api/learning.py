"""
AdaptIQ AI Engine — Enterprise Learning API Endpoints

POST /internal/ai/learn/plan      — Trigger full learning plan (Curator + Study Plan agents)
POST /internal/ai/learn/assess    — Trigger assessment generation
GET  /internal/ai/learn/insights  — Get manager insights (all teams)
GET  /internal/ai/learn/insights/{team_id} — Get insights for specific team
"""

import logging
from fastapi import APIRouter, BackgroundTasks
from app.models.schemas import LearningPlanRequest, AssessmentRequest
from app.engine.orchestrator import run_learning_pipeline, run_assessment_pipeline
from app.engine.insights_agent import generate_manager_insights

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/ai/learn", tags=["enterprise-learning"])


@router.post("/plan")
async def request_learning_plan(
    request: LearningPlanRequest,
    background_tasks: BackgroundTasks,
):
    """
    Accept a learning plan request and launch the multi-agent pipeline:
    1. Learning Path Curator (Foundry IQ)
    2. Study Plan Generator (Fabric IQ + Work IQ)
    3. Engagement recommendations (Work IQ)

    Results are delivered via callback to the Spring Boot gateway.
    """
    logger.info(
        f"Learning plan request — job_id: {request.job_id}, "
        f"role: '{request.role}', goal: '{request.goal}'"
    )

    background_tasks.add_task(
        run_learning_pipeline,
        job_id=request.job_id,
        role=request.role,
        goal=request.goal,
        employee_id=request.employee_id,
        experience_level=request.experience_level,
        weeks_available=request.weeks_available,
    )

    return {
        "status": "accepted",
        "job_id": request.job_id,
        "message": "Learning plan pipeline started (Curator → Study Plan → Engagement agents)",
    }


@router.post("/assess")
async def request_assessment(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks,
):
    """
    Accept an assessment request and launch the Assessment Agent.
    Generates grounded questions from Foundry IQ knowledge base.
    """
    logger.info(
        f"Assessment request — job_id: {request.job_id}, "
        f"cert: '{request.target_certification}', employee: '{request.employee_id}'"
    )

    background_tasks.add_task(
        run_assessment_pipeline,
        job_id=request.job_id,
        target_certification=request.target_certification,
        employee_id=request.employee_id,
    )

    return {
        "status": "accepted",
        "job_id": request.job_id,
        "message": "Assessment pipeline started (Assessment Agent with Foundry IQ grounding)",
    }


@router.get("/insights")
async def get_all_insights():
    """Get Manager Insights Agent output for all teams."""
    logger.info("Manager Insights Agent: generating all-teams insights")
    result = await generate_manager_insights(team_id=None)
    return result


@router.get("/insights/{team_id}")
async def get_team_insights(team_id: str):
    """Get Manager Insights Agent output for a specific team."""
    logger.info(f"Manager Insights Agent: generating insights for team '{team_id}'")
    result = await generate_manager_insights(team_id=team_id)
    return result
