from typing import AsyncGenerator

import httpx

from app.settings import settings


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
        yield client