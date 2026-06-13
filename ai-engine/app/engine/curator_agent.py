"""
AdaptIQ — Learning Path Curator Agent

Retrieves relevant certifications and learning resources from Foundry IQ
and recommends a learning path based on the user's role and target.
Grounded in approved knowledge sources with citations.
"""

import logging
from google import genai
from app.config import settings
from app.services import foundry_client
from app.services.fabric_iq import get_certification_ontology

logger = logging.getLogger(__name__)

CURATOR_SYSTEM_PROMPT = """You are the Learning Path Curator Agent for AdaptIQ, an enterprise learning system.

Your role is to:
1. Map the learner's role and goal to the most relevant certification
2. Retrieve relevant learning resources from Foundry IQ (grounded knowledge)
3. Recommend a structured learning path with clear milestones

Rules:
- ALWAYS cite sources using their Foundry IQ ID (e.g., [FIQ-CERT-AZ204-001])
- Do NOT fabricate information not present in the provided documents
- Be specific about prerequisites, exam domains, and recommended study hours
- Structure your response clearly with sections

Format your response as:
RECOMMENDED_CERTIFICATION: <cert ID and name>
RATIONALE: <why this cert fits the role/goal>
LEARNING_PATH:
<structured path with milestones>
KEY_RESOURCES:
<list of cited resources>
PREREQUISITES:
<list of prerequisites if any>"""


async def curate_learning_path(role: str, goal: str, experience_level: str = "intermediate") -> dict:
    """
    Curate a learning path for a given role and learning goal.

    Args:
        role: The learner's job role (e.g., "Cloud Engineer")
        goal: The learning goal (e.g., "get AZ-204 certified")
        experience_level: beginner/intermediate/advanced

    Returns:
        dict with recommended_certification, learning_path, resources, reasoning
    """
    logger.info(f"Curator Agent: curating path for role='{role}', goal='{goal}'")

    # Step 1: Retrieve relevant docs from Foundry IQ
    search_query = f"{role} {goal} certification learning path requirements"
    docs = await foundry_client.search(search_query, top_k=5)

    # Step 2: Also search for assessment resources
    assess_docs = await foundry_client.search(f"{goal} study guide domains", top_k=3)
    all_docs = docs + [d for d in assess_docs if d.foundry_id not in {x.foundry_id for x in docs}]

    # Step 3: Build context
    docs_context = "\n\n".join(
        f"[{doc.foundry_id}]\n{doc.snippet}"
        for doc in all_docs
    )

    user_prompt = f"""Learner Profile:
- Role: {role}
- Learning Goal: {goal}
- Experience Level: {experience_level}

Foundry IQ Retrieved Knowledge:
{docs_context}

Based ONLY on the above retrieved knowledge, curate a learning path for this learner."""

    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=f"{CURATOR_SYSTEM_PROMPT}\n\n{user_prompt}",
        config={"temperature": 0.3},
    )

    raw_text = response.text.strip()
    logger.info(f"Curator Agent: generated learning path ({len(raw_text)} chars)")

    return {
        "agent": "Learning Path Curator",
        "role": role,
        "goal": goal,
        "output": raw_text,
        "sources_used": [{"id": d.foundry_id, "url": d.source_url} for d in all_docs],
    }
