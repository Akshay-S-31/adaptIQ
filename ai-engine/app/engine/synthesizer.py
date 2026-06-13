"""
AdaptIQ AI Engine — Report Synthesizer

LLM-powered synthesis of retrieved documents into a
structured research report with executive summary,
detailed content, and inline citations.
Uses the official google-genai SDK.
"""

import logging
from google import genai
from app.config import settings
from app.models.schemas import RetrievedDocument, DraftReport

logger = logging.getLogger(__name__)

SYNTHESIZER_SYSTEM_PROMPT = """You are a senior research analyst for AdaptIQ, an enterprise research agent.

Your job is to synthesize retrieved documents into a comprehensive, well-structured research report.

Report structure:
1. **Executive Summary** (2-3 sentences): The key finding and recommendation.
2. **Detailed Content** (3-6 paragraphs): In-depth analysis covering:
   - Core concepts and how they address the query
   - Architectural patterns and best practices
   - Trade-offs and considerations
   - Real-world examples and metrics where available
   - Actionable recommendations

Rules:
- Ground ALL claims in the provided source documents. Reference sources by their Foundry IQ ID (e.g., [FIQ-ARCH-001]).
- Do NOT fabricate information not present in the sources.
- Use professional, enterprise-grade language.
- Be specific with numbers and metrics when available.
- If sources are insufficient, explicitly state what is missing.

Respond in this exact format (no markdown fences):
EXECUTIVE_SUMMARY:
<your executive summary here>

DETAILED_CONTENT:
<your detailed content here>"""


async def synthesize_report(
    query: str,
    documents: list[RetrievedDocument],
    previous_gaps: list[str] | None = None,
) -> DraftReport:
    """
    Synthesize retrieved documents into a structured research report.

    Args:
        query: The original research query
        documents: Retrieved documents from Foundry IQ
        previous_gaps: Gaps identified by the critic in a prior iteration

    Returns:
        DraftReport with executive summary and detailed content
    """
    logger.info(f"Synthesizing report from {len(documents)} documents")

    client = genai.Client(api_key=settings.google_api_key)

    # Build context from retrieved documents
    docs_context = "\n\n".join(
        f"[{doc.foundry_id}] (Source: {doc.source_url})\n{doc.snippet}"
        for doc in documents
    )

    user_prompt = f"""Original Research Query: {query}

Retrieved Documents:
{docs_context}"""

    if previous_gaps:
        gaps_text = "\n".join(f"- {gap}" for gap in previous_gaps)
        user_prompt += f"""

IMPORTANT — The previous draft had these gaps identified by the quality review:
{gaps_text}
Please specifically address these gaps in your revised report."""

    full_prompt = f"{SYNTHESIZER_SYSTEM_PROMPT}\n\n{user_prompt}"

    response = client.models.generate_content(
        model=settings.llm_model,
        contents=full_prompt,
        config={"temperature": 0.4},
    )

    raw_text = response.text.strip()

    # Parse the structured response
    executive_summary = ""
    detailed_content = ""

    if "EXECUTIVE_SUMMARY:" in raw_text and "DETAILED_CONTENT:" in raw_text:
        parts = raw_text.split("DETAILED_CONTENT:")
        executive_summary = parts[0].replace("EXECUTIVE_SUMMARY:", "").strip()
        detailed_content = parts[1].strip()
    else:
        # Fallback: treat the whole response as detailed content
        paragraphs = raw_text.split("\n\n")
        executive_summary = paragraphs[0] if paragraphs else raw_text[:200]
        detailed_content = raw_text

    draft = DraftReport(
        executive_summary=executive_summary,
        detailed_content=detailed_content,
        citations_used=documents,
    )

    logger.info(f"Draft report generated — summary: {len(executive_summary)} chars, detail: {len(detailed_content)} chars")
    return draft
