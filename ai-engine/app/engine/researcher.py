"""
AdaptIQ AI Engine — Research Orchestrator

The core autonomous agent that implements the ReAct + Reflexion loop:

  for iteration in range(max_iterations):
      1. Plan sub-queries from the original query
      2. Execute sub-queries against Foundry IQ
      3. Synthesize findings into a draft report
      4. Reflexion: critique the draft
      5. If critique passes → finalize with citations, break
      6. If critique fails → generate refined sub-queries, continue
"""

import json
import time
import logging
from app.config import settings
from app.models.schemas import (
    RetrievedDocument,
    DraftReport,
    CompletionPayload,
    TraceEntry,
)
from app.engine.planner import plan_sub_queries
from app.engine.synthesizer import synthesize_report
from app.engine.critic import critique_draft
from app.services import foundry_client, gateway_client

logger = logging.getLogger(__name__)


async def run_research_pipeline(job_id: str, query: str) -> None:
    """
    Execute the full ReAct + Reflexion research pipeline.

    This is the top-level entry point called as a background task.
    It orchestrates the planner, Foundry IQ search, synthesizer,
    and critic in a loop, then calls back to the Spring Boot gateway.

    Args:
        job_id: UUID of the research job
        query: The user's research query
    """
    start_time = time.time()
    traces: list[TraceEntry] = []
    all_documents: list[RetrievedDocument] = []
    previous_gaps: list[str] = []
    final_draft: DraftReport | None = None
    final_confidence: float = 0.0

    logger.info(f"═══ Starting research pipeline for job [{job_id}] ═══")
    logger.info(f"Query: {query}")
    logger.info(f"Max iterations: {settings.max_iterations}")

    try:
        for iteration in range(1, settings.max_iterations + 1):
            logger.info(f"─── Iteration {iteration}/{settings.max_iterations} ───")

            # ── Step 1: Plan sub-queries ─────────────────────────
            if iteration == 1:
                sub_queries = await plan_sub_queries(query)
            else:
                # On subsequent iterations, use the critic's suggested queries
                from app.models.schemas import SubQuery
                sub_queries = [
                    SubQuery(question=sq, rationale="Follow-up from critique")
                    for sq in previous_gaps[:3]  # Limit to 3 follow-ups
                ]
                if not sub_queries:
                    sub_queries = await plan_sub_queries(query)

            traces.append(TraceEntry(
                iteration_number=iteration,
                action_taken="PLAN_QUERIES",
                action_input=query if iteration == 1 else f"Gaps: {previous_gaps}",
                observation=f"Generated {len(sub_queries)} sub-queries: "
                            + ", ".join(sq.question[:50] for sq in sub_queries),
            ))

            # ── Step 2: Execute sub-queries against Foundry IQ ──
            iteration_docs: list[RetrievedDocument] = []
            for sq in sub_queries:
                docs = await foundry_client.search(sq.question, top_k=3)
                iteration_docs.extend(docs)

            # Deduplicate by foundry_id
            seen_ids = {doc.foundry_id for doc in all_documents}
            new_docs = [d for d in iteration_docs if d.foundry_id not in seen_ids]
            all_documents.extend(new_docs)

            traces.append(TraceEntry(
                iteration_number=iteration,
                action_taken="FOUNDRY_SEARCH",
                action_input=", ".join(sq.question for sq in sub_queries),
                observation=f"Retrieved {len(new_docs)} new documents "
                            f"({len(all_documents)} total)",
            ))

            # ── Step 3: Synthesize draft report ──────────────────
            final_draft = await synthesize_report(
                query=query,
                documents=all_documents,
                previous_gaps=previous_gaps if iteration > 1 else None,
            )

            traces.append(TraceEntry(
                iteration_number=iteration,
                action_taken="SYNTHESIZE",
                action_input=f"{len(all_documents)} documents",
                observation=f"Draft: {len(final_draft.executive_summary)} char summary, "
                            f"{len(final_draft.detailed_content)} char detail",
            ))

            # ── Step 4: Reflexion — critique the draft ───────────
            critique = await critique_draft(
                original_query=query,
                executive_summary=final_draft.executive_summary,
                detailed_content=final_draft.detailed_content,
                iteration=iteration,
            )

            final_confidence = critique.confidence_score

            traces.append(TraceEntry(
                iteration_number=iteration,
                action_taken="SELF_CRITIQUE",
                action_input=f"Draft v{iteration}",
                observation=f"Confidence: {critique.confidence_score}%, "
                            f"Passed: {critique.passed}, "
                            f"Gaps: {critique.gaps}",
            ))

            # ── Step 5: Break or refine ──────────────────────────
            if critique.passed:
                logger.info(
                    f"✓ Critique PASSED at iteration {iteration} "
                    f"with {critique.confidence_score}% confidence"
                )
                break
            else:
                logger.info(
                    f"✗ Critique FAILED at iteration {iteration} — "
                    f"gaps: {critique.gaps}"
                )
                previous_gaps = critique.suggested_queries or critique.gaps

        # ── Finalize and callback ────────────────────────────────
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Build citations JSON
        citations = json.dumps([
            {
                "source_url": doc.source_url,
                "snippet": doc.snippet,
                "foundry_id": doc.foundry_id,
            }
            for doc in all_documents
        ])

        payload = CompletionPayload(
            executiveSummary=final_draft.executive_summary,
            detailedContent=final_draft.detailed_content,
            confidenceScore=round(final_confidence, 2),
            citations=citations,
            iterationCount=min(iteration, settings.max_iterations),
            processingTimeMs=elapsed_ms,
            traces=traces,
        )

        logger.info(
            f"═══ Pipeline complete for job [{job_id}] ═══\n"
            f"  Confidence: {final_confidence}%\n"
            f"  Iterations: {iteration}\n"
            f"  Documents: {len(all_documents)}\n"
            f"  Time: {elapsed_ms}ms"
        )

        await gateway_client.report_completion(job_id, payload)

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        error_msg = f"Research pipeline failed at iteration: {str(e)}"
        logger.exception(f"Pipeline error for job [{job_id}]: {error_msg}")
        await gateway_client.report_failure(job_id, error_msg)
