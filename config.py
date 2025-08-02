"""Application configuration using environment variables.

This module loads values from a `.env` file and exposes them via a
`Settings` object. Adjust defaults and add error handling as necessary
for your environment.
"""

from dotenv import load_dotenv
from pydantic import BaseSettings

# Load variables from .env file into the environment
load_dotenv()


class Settings(BaseSettings):
    """Configuration values for external services."""

    payping_client_id: str
    payping_client_secret: str
    nobitex_api_key: str
    nobitex_api_secret: str | None = None
    nobitex_base_url: str = "https://api.nobitex.ir"
    testnet: bool = False


# Expose a singleton settings object
settings = Settings()
