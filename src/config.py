"""Configuration management for MCP server."""

import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl, field_validator


logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Application configuration loaded from environment variables.

    All settings can be overridden via environment variables.
    Example: N8N_URL=http://localhost:5678
    """

    # n8n Configuration
    n8n_url: str = Field(
        ...,
        description="Base URL for n8n instance (e.g., http://localhost:5678)",
        alias="N8N_URL"
    )
    n8n_api_key: str = Field(
        ...,
        description="API key for n8n authentication",
        alias="N8N_API_KEY"
    )
    n8n_timeout: int = Field(
        default=30,
        description="Timeout in seconds for n8n API requests",
        alias="N8N_TIMEOUT"
    )
    n8n_max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed n8n API requests",
        alias="N8N_MAX_RETRIES"
    )

    # MCP Server Configuration
    mcp_server_host: str = Field(
        default="0.0.0.0",
        description="Host to bind MCP server to",
        alias="MCP_SERVER_HOST"
    )
    mcp_server_port: int = Field(
        default=8001,
        description="Port to bind MCP server to",
        alias="MCP_SERVER_PORT"
    )
    management_api_port: int = Field(
        default=8002,
        description="Port for management REST API",
        alias="MANAGEMENT_API_PORT"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        alias="LOG_LEVEL"
    )
    log_format: str = Field(
        default="json",
        description="Log format: 'json' or 'console'",
        alias="LOG_FORMAT"
    )

    # Security Configuration
    mcp_auth_token: Optional[str] = Field(
        default=None,
        description="Optional authentication token for MCP server",
        alias="MCP_AUTH_TOKEN"
    )

    # Django Integration (Optional)
    django_portal_url: Optional[str] = Field(
        default=None,
        description="Optional Django portal URL for webhook integration",
        alias="DJANGO_PORTAL_URL"
    )
    django_webhook_token: Optional[str] = Field(
        default=None,
        description="Optional webhook token for Django integration",
        alias="DJANGO_WEBHOOK_TOKEN"
    )

    # Performance Configuration
    enable_caching: bool = Field(
        default=True,
        description="Enable caching for workflow list and details",
        alias="ENABLE_CACHING"
    )
    cache_ttl: int = Field(
        default=60,
        description="Cache TTL in seconds",
        alias="CACHE_TTL"
    )

    # Rate Limiting
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable rate limiting for API requests",
        alias="ENABLE_RATE_LIMITING"
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per minute",
        alias="RATE_LIMIT_REQUESTS"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format is valid."""
        valid_formats = ["json", "console"]
        v_lower = v.lower()
        if v_lower not in valid_formats:
            raise ValueError(f"Log format must be one of {valid_formats}")
        return v_lower

    @field_validator("n8n_url")
    @classmethod
    def validate_n8n_url(cls, v: str) -> str:
        """Validate and normalize n8n URL."""
        # Remove trailing slash
        return v.rstrip("/")

    def get_n8n_api_base_url(self) -> str:
        """Get the complete n8n API base URL."""
        return f"{self.n8n_url}/api/v1"

    def get_n8n_headers(self) -> dict[str, str]:
        """Get headers for n8n API requests."""
        return {
            "X-N8N-API-KEY": self.n8n_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def is_django_integration_enabled(self) -> bool:
        """Check if Django integration is configured."""
        return bool(self.django_portal_url and self.django_webhook_token)

    def model_post_init(self, __context: object) -> None:
        """Post-initialization hook to log configuration."""
        logger.info(
            "Configuration loaded",
            extra={
                "n8n_url": self.n8n_url,
                "mcp_host": self.mcp_server_host,
                "mcp_port": self.mcp_server_port,
                "log_level": self.log_level,
                "caching_enabled": self.enable_caching,
                "rate_limiting_enabled": self.enable_rate_limiting,
                "django_integration": self.is_django_integration_enabled()
            }
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global configuration instance.

    Returns:
        Config: Global configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset global configuration (mainly for testing)."""
    global _config
    _config = None
