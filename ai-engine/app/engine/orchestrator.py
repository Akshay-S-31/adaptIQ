"""
AdaptIQ AI Engine — Multi-Agent Orchestrator

Coordinates the 5 specialized enterprise learning agents in sequence:
1. Learning Path Curator — retrieves grounded learning resources (Foundry IQ)
2. Study Plan Generator — builds capacity-aware schedule (Fabric IQ + Work IQ)
3. Assessment Agent — generates evaluation questions (Foundry IQ)
4. Manager Insights Agent — surfaces team analytics (Fabric IQ + Work IQ)

Also contains the legacy research pipeline for backwards compatibility.
"""

import json
import time
import logging
import httpx
from app.config import settings
from app.engine.curator_agent import curate_learning_path
from app.engine.study_plan_agent import generate_study_plan
from app.engine.assessment_agent import generate_assessment

logger = logging.getLogger(__name__)

GATEWAY_BASE = settings.gateway_base_url


async def _callback_success(job_id: str, payload: dict):
    """Send results back to the Spring Boot gateway."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{GATEWAY_BASE}/internal/jobs/{job_id}/complete",
                json=payload,
            )
            resp.raise_for_status()
            logger.info(f"Job [{job_id}] callback sent successfully")
        except Exception as e:
            logger.error(f"Job [{job_id}] callback failed: {e}")


async def _callback_failure(job_id: str, error: str):
    """Send failure notification back to the Spring Boot gateway."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            await client.post(
                f"{GATEWAY_BASE}/internal/jobs/{job_id}/fail",
                json={"error": error},
            )
        except Exception as e:
            logger.error(f"Job [{job_id}] failure callback failed: {e}")


async def run_learning_pipeline(
    job_id: str,
    role: str,
    goal: str,
    employee_id: str = "EMP-1001",
    experience_level: str = "intermediate",
    weeks_available: int = 6,
):
    """
    Multi-agent learning plan pipeline:
    Agent 1: Learning Path Curator  (Foundry IQ)
    Agent 2: Study Plan Generator   (Fabric IQ + Work IQ)

    Results sent to Gateway via callback.
    """
    start_time = time.time()
    logger.info(f"═══ Starting learning pipeline for job [{job_id}] ═══")

    try:
        # ── Agent 1: Learning Path Curator ────────────────────────────
        logger.info(f"[{job_id}] Agent 1: Learning Path Curator")
        curator_result = await curate_learning_path(
            role=role,
            goal=goal,
            experience_level=experience_level,
        )

        # ── Agent 2: Study Plan Generator ─────────────────────────────
        # Extract certification from the curator output or fall back to goal keyword
        cert_id = _extract_cert_from_goal(goal)
        logger.info(f"[{job_id}] Agent 2: Study Plan Generator (cert={cert_id})")
        study_plan_result = await generate_study_plan(
            role=role,
            target_certification=cert_id,
            employee_id=employee_id,
            weeks_available=weeks_available,
        )

        # ── Build combined report ──────────────────────────────────────
        elapsed = int((time.time() - start_time) * 1000)

        executive_summary = (
            f"Learning path curated for {role} targeting {cert_id}. "
            f"A {weeks_available}-week study plan has been generated using Work IQ "
            f"capacity signals and Fabric IQ certification data."
        )

        detailed_content = (
            f"## Learning Path (Agent 1: Curator)\n\n"
            f"{curator_result['output']}\n\n"
            f"---\n\n"
            f"## Study Plan (Agent 2: Study Plan Generator)\n\n"
            f"{study_plan_result['output']}"
        )

        all_sources = curator_result.get("sources_used", [])
        citations_json = json.dumps(all_sources)

        payload = {
            "executiveSummary": executive_summary,
            "detailedContent": detailed_content,
            "confidenceScore": 85.0,  # Deterministic agents produce high-confidence output
            "citations": citations_json,
            "iterationCount": 2,  # 2 agents executed
            "processingTimeMs": elapsed,
            "traces": [
                {
                    "iterationNumber": 1,
                    "actionTaken": "CURATOR_AGENT",
                    "actionInput": f"role={role}, goal={goal}",
                    "observation": f"Learning path curated with {len(all_sources)} Foundry IQ sources",
                },
                {
                    "iterationNumber": 2,
                    "actionTaken": "STUDY_PLAN_AGENT",
                    "actionInput": f"cert={cert_id}, employee={employee_id}, weeks={weeks_available}",
                    "observation": f"Study plan generated using Work IQ + Fabric IQ data",
                },
            ],
        }

        await _callback_success(job_id, payload)
        logger.info(f"═══ Learning pipeline complete for job [{job_id}] in {elapsed}ms ═══")

    except Exception as e:
        logger.error(f"Learning pipeline failed for job [{job_id}]: {e}", exc_info=True)
        await _callback_failure(job_id, str(e))


async def run_assessment_pipeline(
    job_id: str,
    target_certification: str,
    employee_id: str = "EMP-1001",
):
    """
    Assessment Agent pipeline.
    Generates grounded questions from Foundry IQ.
    """
    start_time = time.time()
    logger.info(f"═══ Starting assessment pipeline for job [{job_id}] ═══")

    try:
        result = await generate_assessment(
            target_certification=target_certification,
            employee_id=employee_id,
        )

        elapsed = int((time.time() - start_time) * 1000)
        output = result["output"]

        # Format questions as readable text
        if isinstance(output, dict) and "questions" in output:
            questions_text = "\n\n".join(
                f"**Q{q['id']}: {q['question']}**\n"
                f"A: {q['options'].get('A', '')}\n"
                f"B: {q['options'].get('B', '')}\n"
                f"C: {q['options'].get('C', '')}\n"
                f"D: {q['options'].get('D', '')}\n"
                f"✓ Correct: {q['correct_answer']} — {q['explanation']}\n"
                f"Source: [{q.get('source', 'N/A')}]"
                for q in output["questions"]
            )
            readiness = output.get("readiness_assessment", "")
            detailed_content = f"## Assessment Questions for {target_certification}\n\n{questions_text}"
            executive_summary = readiness or f"Assessment generated for {target_certification} with {len(output['questions'])} grounded questions."
        else:
            detailed_content = str(output.get("raw", output))
            executive_summary = f"Assessment generated for {target_certification}."

        payload = {
            "executiveSummary": executive_summary,
            "detailedContent": detailed_content,
            "confidenceScore": 90.0,
            "citations": json.dumps(result.get("sources_used", [])),
            "iterationCount": 1,
            "processingTimeMs": elapsed,
            "traces": [
                {
                    "iterationNumber": 1,
                    "actionTaken": "ASSESSMENT_AGENT",
                    "actionInput": f"cert={target_certification}, employee={employee_id}",
                    "observation": f"Generated grounded questions from {len(result.get('sources_used', []))} Foundry IQ sources",
                }
            ],
        }

        await _callback_success(job_id, payload)
        logger.info(f"═══ Assessment pipeline complete for job [{job_id}] in {elapsed}ms ═══")

    except Exception as e:
        logger.error(f"Assessment pipeline failed for job [{job_id}]: {e}", exc_info=True)
        await _callback_failure(job_id, str(e))


def _extract_cert_from_goal(goal: str) -> str:
    """Simple heuristic to extract a cert ID from the learning goal string."""
    goal_upper = goal.upper()
    for cert in ["AZ-204", "AZ-400", "AZ-104", "AZ-305", "AZ-500", "DP-203", "DP-300"]:
        if cert in goal_upper:
            return cert
    # Default fallback
    return "AZ-204"


# ─── Legacy Research Pipeline (kept for backward compatibility) ──────────────

async def run_research_pipeline(job_id: str, query: str):
    """
    Legacy research pipeline. Delegates to the learning pipeline
    by interpreting the query as a learning goal.
    """
    logger.info(f"Legacy research pipeline invoked for job [{job_id}] — routing to learning pipeline")
    await run_learning_pipeline(
        job_id=job_id,
        role="Professional",
        goal=query,
        employee_id="EMP-1001",
    )
