"""
AdaptIQ — Assessment Agent

Generates grounded practice questions from Foundry IQ knowledge sources
and evaluates learner readiness. Questions are always cited to approved
knowledge documents.
"""

import json
import logging
from google import genai
from app.config import settings
from app.services import foundry_client
from app.services.fabric_iq import get_learner_by_employee, get_certification_ontology

logger = logging.getLogger(__name__)

ASSESSMENT_SYSTEM_PROMPT = """You are the Assessment Agent for AdaptIQ, an enterprise learning system.

Your role is to generate grounded assessment questions from the provided Foundry IQ knowledge
and evaluate learner readiness for certification.

Rules:
- Generate 5 multiple-choice questions ONLY from the provided source documents
- Each question MUST cite its source with the Foundry IQ ID (e.g., Source: [FIQ-CERT-AZ204-001])
- Questions should reflect the real exam domains proportionally
- Include the correct answer and a brief explanation
- Do NOT fabricate questions not grounded in the provided documents

Format your response as valid JSON:
{
  "certification": "<cert ID>",
  "questions": [
    {
      "id": 1,
      "question": "<question text>",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correct_answer": "A",
      "explanation": "<why this answer is correct>",
      "source": "<Foundry IQ ID>"
    }
  ],
  "readiness_assessment": "<brief assessment of learner readiness based on their profile>"
}"""


async def generate_assessment(
    target_certification: str,
    employee_id: str = "EMP-1001",
) -> dict:
    """
    Generate grounded assessment questions for a certification.

    Args:
        target_certification: Target cert (e.g., "AZ-204")
        employee_id: Employee ID for personalized assessment

    Returns:
        dict with questions, answers, and readiness assessment
    """
    logger.info(f"Assessment Agent: generating assessment for cert='{target_certification}', employee='{employee_id}'")

    # Step 1: Retrieve assessment material from Foundry IQ
    docs = await foundry_client.search(f"{target_certification} assessment questions sample quiz", top_k=4)
    domain_docs = await foundry_client.search(f"{target_certification} study guide domains", top_k=3)
    all_docs = docs + [d for d in domain_docs if d.foundry_id not in {x.foundry_id for x in docs}]

    docs_context = "\n\n".join(
        f"[{doc.foundry_id}]\n{doc.snippet}"
        for doc in all_docs
    )

    # Step 2: Fabric IQ — get learner profile for personalization
    learner = get_learner_by_employee(employee_id)
    cert = get_certification_ontology(target_certification)

    learner_context = ""
    if learner:
        learner_context = f"""
Learner Profile (Fabric IQ):
- Current Practice Score: {learner['practice_score_avg']}%
- Skill Gaps: {', '.join(learner['skill_gaps']) if learner['skill_gaps'] else 'None'}
- Strengths: {', '.join(learner['strengths'])}
Please include questions that specifically target the learner's identified skill gaps."""

    user_prompt = f"""Target Certification: {target_certification}
{f'Cert Skills: {", ".join(cert["skills"])}' if cert else ''}

{learner_context}

Foundry IQ Knowledge Sources:
{docs_context}

Generate 5 grounded assessment questions from the above sources only. Return valid JSON."""

    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=f"{ASSESSMENT_SYSTEM_PROMPT}\n\n{user_prompt}",
        config={"temperature": 0.2},
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("```", 1)[0]
    raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        logger.info(f"Assessment Agent: generated {len(parsed.get('questions', []))} questions")
        return {
            "agent": "Assessment Agent",
            "target_certification": target_certification,
            "employee_id": employee_id,
            "output": parsed,
            "sources_used": [{"id": d.foundry_id, "url": d.source_url} for d in all_docs],
        }
    except json.JSONDecodeError as e:
        logger.warning(f"Assessment Agent: failed to parse JSON, returning raw: {e}")
        return {
            "agent": "Assessment Agent",
            "target_certification": target_certification,
            "employee_id": employee_id,
            "output": {"raw": raw_text, "error": "Could not parse structured response"},
            "sources_used": [{"id": d.foundry_id, "url": d.source_url} for d in all_docs],
        }
