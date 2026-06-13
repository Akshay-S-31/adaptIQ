"""
AdaptIQ AI Engine — Gateway Callback Client

Async HTTP client to call back to the Spring Boot gateway
when a research job completes or fails.
"""

import logging
import httpx
from app.config import settings
from app.models.schemas import CompletionPayload, FailurePayload

logger = logging.getLogger(__name__)


async def report_completion(job_id: str, payload: CompletionPayload) -> None:
    """
    Send the completed report back to Spring Boot.
    PUT /internal/jobs/{job_id}/complete
    """
    url = f"{settings.gateway_base_url}/internal/jobs/{job_id}/complete"
    logger.info(f"Sending completion callback for job [{job_id}] to {url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.put(
            url,
            json=payload.model_dump(by_alias=True),
        )
        response.raise_for_status()
        logger.info(f"Gateway accepted completion for job [{job_id}] — HTTP {response.status_code}")


async def report_failure(job_id: str, error_message: str) -> None:
    """
    Notify Spring Boot that a job has failed.
    PUT /internal/jobs/{job_id}/fail
    """
    url = f"{settings.gateway_base_url}/internal/jobs/{job_id}/fail"
    logger.error(f"Sending failure callback for job [{job_id}]: {error_message}")

    payload = FailurePayload(error=error_message)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.put(url, json=payload.model_dump())
            response.raise_for_status()
            logger.info(f"Gateway accepted failure for job [{job_id}]")
        except Exception as e:
            logger.error(f"Failed to report failure to gateway for job [{job_id}]: {e}")
