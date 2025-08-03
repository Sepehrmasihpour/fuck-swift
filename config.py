"""Configuration module for application settings.

This module loads environment variables from a ``.env`` file using
``python-dotenv`` and exposes a :data:`settings` object for use across the
project.
"""

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Load variables from .env into environment
load_dotenv()


class Settings(BaseSettings):
    """Application settings derived from environment variables."""

    payping_client_id: str = Field(..., env="PAYPING_CLIENT_ID")
    payping_client_secret: str = Field(..., env="PAYPING_CLIENT_SECRET")
    nobitex_api_key: str = Field(..., env="NOBITEX_API_KEY")
    nobitex_base_url: str = Field(..., env="NOBITEX_BASE_URL")
    nobitex_sheba: str = Field(..., env="NOBITEX_SHEBA")
    rpc_url: str = Field(..., env="RPC_URL")
    foregign_hot_wallet_address: str = Field(..., env="FOREIGN_HOT_WALLET_ADDRESS")


# Instantiate a global settings object
settings = Settings()
