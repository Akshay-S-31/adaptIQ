"""
AdaptIQ AI Engine — Configuration

Reads all settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Gemini
    google_api_key: str = Field(..., description="Google AI Studio API key")
    llm_model: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    llm_temperature: float = Field(default=0.3, description="LLM temperature for reasoning")

    # Spring Boot Gateway
    gateway_base_url: str = Field(
        default="http://localhost:8080",
        description="Base URL of the Spring Boot gateway"
    )

    # Research Loop
    max_iterations: int = Field(
        default=3,
        description="Maximum number of ReAct + Reflexion iterations"
    )
    confidence_threshold: float = Field(
        default=75.0,
        description="Minimum confidence score to pass critique (0-100)"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()
