"""Analyze endpoints for log processing."""

import json

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..analyze.models import LogRequest
from ..dependencies import get_settings
from ..services.ai_service import ai_service
from ..settings import Settings

MODEL = "qwen2.5:0.5b"

router = APIRouter(
    prefix="/analyze",
)


@router.post("/")
async def analyze_log(
    request: LogRequest, locale: str = "en", settings: Settings = Depends(get_settings)
):
    """Analyze log content and stream diagnostic results.

    Parameters
    ----------
    request : LogRequest
        Payload containing the log content to analyze.
    locale : str, optional
        Language for the LLM response. Defaults to "en".

    Yields
    ------
    JSON lines
        Streaming NDJSON responses with diagnostic stages.
    """

    async def generator():
        # Inform client that search is starting
        yield json.dumps({"status": "searching"}) + "\n"

        procedure_obj = ai_service.find_best_procedure(request.content)

        if procedure_obj:
            yield (
                json.dumps(
                    {
                        "status": "procedure_found",
                        "procedure_title": procedure_obj.get("title")
                        if procedure_obj
                        else None,
                        "procedure_content": procedure_obj.get("content")
                        if procedure_obj
                        else None,
                    }
                )
                + "\n"
            )

        yield json.dumps({"status": "reasoning"}) + "\n"

        system_prompt = (
            "Act as a Senior SRE. Use the provided RAG procedure to diagnose the logs. "
            f"Language: {locale}. "
            "Rules: "
            "1. Respond ONLY in valid JSON. "
            "2. Use these keys: 'status' (CRITICAL/WARNING), 'service', "
            "'namespace', 'cause', 'solution'. "
            "3. Keep the 'solution' actionable and technical."
            "4. EVERY value must be a simple string. NO nested objects or "
            "braces {} inside values."
        )

        print("System Prompt:", system_prompt)

        proc_text = (
            procedure_obj.get("content", "No specific procedure found.")
            if procedure_obj
            else "No specific procedure found."
        )

        user_content = f"PROCEDURE: {proc_text}\nLOGS:\n{request.content}"

        print("User Content:", user_content)

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "format": "json",
            "stream": True,
            "options": {"temperature": 0.1},
        }

        client = httpx.AsyncClient()
        async with client.stream(
            "POST",
            f"{settings.ollama_url}/chat",
            json=payload,
        ) as response:
            fullContent = ""
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    fullContent += content
                    yield json.dumps({"status": "streaming", "chunk": content}) + "\n"

            print("Final Response:", fullContent)

    return StreamingResponse(generator(), media_type="application/x-ndjson")
