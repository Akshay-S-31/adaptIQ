"""
AdaptIQ AI Engine — FastAPI Application

The autonomous research agent powered by Google Gemini 3.5 Flash.
Implements the ReAct + Reflexion loop for self-improving research.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

from app.config import settings
from app.api.synthesize import router as synthesize_router
from app.api.learning import router as learning_router

# ─── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-30s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ───────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("═══════════════════════════════════════════════════")
    logger.info("  AdaptIQ Enterprise Learning Engine starting")
    logger.info(f"  Model: {settings.llm_model}")
    logger.info(f"  Gateway: {settings.gateway_base_url}")
    logger.info("  Agents: Curator | Study Plan | Assessment | Insights")
    logger.info("  IQ Layers: Foundry IQ | Work IQ | Fabric IQ")
    logger.info("═══════════════════════════════════════════════════")
    yield
    logger.info("AdaptIQ AI Engine shutting down")


# ─── App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="AdaptIQ Enterprise Learning Engine",
    description="Multi-agent enterprise learning system with Foundry IQ, Work IQ, and Fabric IQ",
    version="2.0.0",
    lifespan=lifespan,
)

# Mount routers
app.include_router(synthesize_router)
app.include_router(learning_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model": settings.llm_model,
        "max_iterations": settings.max_iterations,
    }
