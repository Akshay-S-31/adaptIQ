"""
AdaptIQ AI Engine — Query Planner

LLM-powered decomposition of complex research queries
into targeted sub-queries for Foundry IQ retrieval.
Uses the official google-genai SDK.
"""

import json
import logging
from google import genai
from app.config import settings
from app.models.schemas import SubQuery

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are a research planning assistant for AdaptIQ, an enterprise research agent.

Your job is to decompose a complex research query into 3-5 specific, targeted sub-queries that can be searched against a knowledge base.

Rules:
1. Each sub-query should target ONE specific aspect of the original query.
2. Sub-queries should be phrased as clear search queries, not questions.
3. Cover different angles: architecture, best practices, trade-offs, real-world examples, metrics.
4. Include a brief rationale for why each sub-query matters.

Respond ONLY with a valid JSON array. No markdown, no code fences, no extra text.
Example format:
[
  {"question": "event-driven architecture patterns for real-time processing", "rationale": "Covers the core architectural approach"},
  {"question": "Apache Kafka vs RabbitMQ throughput comparison", "rationale": "Compares specific technologies"}
]"""


async def plan_sub_queries(query: str) -> list[SubQuery]:
    """
    Decompose a research query into targeted sub-queries.

    Args:
        query: The user's original research query

    Returns:
        List of SubQuery objects
    """
    logger.info(f"Planning sub-queries for: '{query[:80]}...'")

    client = genai.Client(api_key=settings.google_api_key)

    full_prompt = f"{PLANNER_SYSTEM_PROMPT}\n\nDecompose this research query into sub-queries:\n\n{query}"

    response = client.models.generate_content(
        model=settings.llm_model,
        contents=full_prompt,
        config={"temperature": settings.llm_temperature},
    )

    raw_text = response.text.strip()

    # Clean up potential markdown code fences
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("```", 1)[0]
    raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        sub_queries = [SubQuery(**item) for item in parsed]
        logger.info(f"Planned {len(sub_queries)} sub-queries")
        return sub_queries
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse planner output, using fallback: {e}")
        return [SubQuery(
            question=query,
            rationale="Fallback: original query used directly"
        )]
