from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    app_name: str = "API"

@lru_cache
def get_settings() -> Settings:
    return Settings()
