from fastapi import Depends
from .settings import Settings

# Dependency that returns a Settings instance.  FastAPI will call this on each request.
# Using a function keeps the Settings object local and allows future caching if desired.
def get_settings() -> Settings:
    return Settings()
