"""
AdaptIQ — Study Plan Generator Agent

Converts a recommended learning path into a practical, capacity-aware
study schedule. Integrates Fabric IQ (certification requirements, learner data)
and Work IQ (workload signals, calendar availability) to produce realistic plans.
"""

import logging
from google import genai
from app.config import settings
from app.services.fabric_iq import get_certification_ontology, get_learner_by_employee
from app.services.work_iq import recommend_study_slots

logger = logging.getLogger(__name__)

STUDY_PLAN_SYSTEM_PROMPT = """You are the Study Plan Generator Agent for AdaptIQ, an enterprise learning system.

Your role is to convert a learning path into a practical, week-by-week study schedule
that accounts for the learner's workload, focus time, and skill gaps.

Rules:
- Use the Fabric IQ data (certification requirements, learner profile, skill gaps) to set targets
- Use the Work IQ data (meeting load, focus hours, preferred slot) to schedule realistically
- Produce a week-by-week plan with daily study hours and specific topics
- Set clear milestone checkpoints (e.g., "complete Module 4 by Week 3")
- Flag if the workload is too high to complete the certification in the target timeline

Format your response as:
STUDY_TIMELINE: <e.g., "6 weeks" or "8 weeks">
DAILY_STUDY_HOURS: <e.g., "1 hour/day">
RECOMMENDED_SLOT: <e.g., "Morning 9-10 AM on Mon/Wed/Fri">
WEEK_BY_WEEK_PLAN:
<Week 1: ...>
<Week 2: ...>
...
MILESTONES:
<list of checkpoints>
RISK_FLAGS:
<any capacity or timeline risks>"""


async def generate_study_plan(
    role: str,
    target_certification: str,
    employee_id: str = "EMP-1001",
    weeks_available: int = 6,
) -> dict:
    """
    Generate a capacity-aware study plan.

    Args:
        role: Learner's job role
        target_certification: Target cert (e.g., "AZ-204")
        employee_id: Employee ID for Work IQ lookup
        weeks_available: Target completion timeline

    Returns:
        dict with study plan output and metadata
    """
    logger.info(f"Study Plan Agent: generating plan for cert='{target_certification}', employee='{employee_id}'")

    # Step 1: Fabric IQ — get certification requirements
    cert_data = get_certification_ontology(target_certification)
    cert_context = ""
    if cert_data:
        cert_context = f"""Fabric IQ — Certification Ontology:
- Certification: {cert_data['name']} ({cert_data['id']})
- Required Skills: {', '.join(cert_data['skills'])}
- Recommended Study Hours: {cert_data['recommended_hours']}
- Pass Score Threshold: {cert_data['pass_threshold_score']}%
- Difficulty: {cert_data['difficulty']}
- Prerequisites: {', '.join(cert_data['prerequisites']) if cert_data['prerequisites'] else 'None'}"""

    # Step 2: Fabric IQ — get learner profile if exists
    learner_data = get_learner_by_employee(employee_id)
    learner_context = ""
    if learner_data:
        learner_context = f"""Fabric IQ — Learner Profile:
- Current Readiness Score: {learner_data['readiness_score']}/100
- Hours Already Studied: {learner_data['hours_studied']}
- Modules Completed: {learner_data['modules_completed']}/{learner_data['total_modules']}
- Practice Score Average: {learner_data['practice_score_avg']}%
- Skill Gaps: {', '.join(learner_data['skill_gaps']) if learner_data['skill_gaps'] else 'None identified'}
- Strengths: {', '.join(learner_data['strengths'])}"""

    # Step 3: Work IQ — get schedule recommendations
    work_rec = recommend_study_slots(employee_id)
    work_context = f"""Work IQ — Workplace Signals:
- Recommended Daily Study Hours: {work_rec['suggested_daily_hours']} hours
- Best Study Slot: {work_rec['suggested_slot']}
- Low-Meeting Day: {work_rec['low_meeting_day']}
- Capacity Risk Level: {work_rec['risk_level']}
- Work IQ Recommendation: {work_rec['recommendation']}"""

    user_prompt = f"""Learner: {role} targeting {target_certification}
Target Timeline: {weeks_available} weeks

{cert_context}

{learner_context}

{work_context}

Generate a realistic, week-by-week study plan that accounts for the learner's capacity and skill gaps."""

    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=f"{STUDY_PLAN_SYSTEM_PROMPT}\n\n{user_prompt}",
        config={"temperature": 0.3},
    )

    raw_text = response.text.strip()
    logger.info(f"Study Plan Agent: generated plan ({len(raw_text)} chars)")

    return {
        "agent": "Study Plan Generator",
        "target_certification": target_certification,
        "employee_id": employee_id,
        "weeks_available": weeks_available,
        "output": raw_text,
        "fabric_iq_data": cert_data,
        "work_iq_data": work_rec,
    }
