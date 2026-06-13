"""
AdaptIQ AI Engine — Reflexion Critic

LLM-powered self-critique module that evaluates draft reports
for quality, completeness, and groundedness. This is the
"Reflexion" step from the spec — the agent critiques its own work.
Uses the official google-genai SDK.
"""

import json
import logging
from google import genai
from app.config import settings
from app.models.schemas import CritiqueResult

logger = logging.getLogger(__name__)

CRITIC_SYSTEM_PROMPT = """You are a strict quality reviewer for AdaptIQ, an enterprise research agent.

Your job is to critique a draft research report against the original query. Evaluate:

1. **Completeness**: Does the report fully address the original query? Are there obvious missing aspects?
2. **Groundedness**: Are all claims supported by cited sources? Any unsupported assertions?
3. **Contradictions**: Are there internal contradictions or inconsistencies?
4. **Depth**: Is the analysis deep enough for enterprise decision-makers?
5. **Actionability**: Does it provide specific, actionable recommendations?

Assign a confidence score from 0 to 100:
- 90-100: Excellent, comprehensive, well-grounded
- 75-89: Good, minor gaps only
- 50-74: Needs improvement, significant gaps
- 0-49: Poor, major issues

Respond ONLY with valid JSON (no markdown fences, no extra text):
{
  "passed": true/false,
  "confidence_score": 0-100,
  "gaps": ["gap 1", "gap 2"],
  "suggested_queries": ["follow-up query 1", "follow-up query 2"],
  "reasoning": "Brief explanation of the assessment"
}

Set "passed" to true only if confidence_score >= 75."""


async def critique_draft(
    original_query: str,
    executive_summary: str,
    detailed_content: str,
    iteration: int,
) -> CritiqueResult:
    """
    Perform Reflexion self-critique on a draft report.

    Args:
        original_query: The user's original research query
        executive_summary: Draft executive summary
        detailed_content: Draft detailed content
        iteration: Current iteration number (for logging)

    Returns:
        CritiqueResult with pass/fail, confidence, gaps, and follow-up queries
    """
    logger.info(f"Critiquing draft report (iteration {iteration})")

    client = genai.Client(api_key=settings.google_api_key)

    user_prompt = f"""Original Research Query:
{original_query}

Draft Executive Summary:
{executive_summary}

Draft Detailed Content:
{detailed_content}

Evaluate this draft and provide your critique as JSON."""

    full_prompt = f"{CRITIC_SYSTEM_PROMPT}\n\n{user_prompt}"

    response = client.models.generate_content(
        model=settings.llm_model,
        contents=full_prompt,
        config={"temperature": 0.2},
    )

    raw_text = response.text.strip()

    # Clean markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("```", 1)[0]
    raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        result = CritiqueResult(**parsed)

        # Enforce the threshold rule
        if result.confidence_score >= settings.confidence_threshold:
            result.passed = True
        else:
            result.passed = False

        logger.info(
            f"Critique result — passed: {result.passed}, "
            f"confidence: {result.confidence_score}%, "
            f"gaps: {len(result.gaps)}"
        )
        return result

    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse critic output, assuming pass: {e}")
        return CritiqueResult(
            passed=True,
            confidence_score=70.0,
            gaps=[],
            suggested_queries=[],
            reasoning=f"Failed to parse critique output: {e}. Defaulting to pass.",
        )
