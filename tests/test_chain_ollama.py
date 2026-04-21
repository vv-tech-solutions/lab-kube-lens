import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app

@pytest.mark.asyncio
async def test_chain_ollama_success(monkeypatch):
    # Mock Ollama’s response
    async def mock_post(url, json, timeout):
        class MockResponse:
            status_code = 200
            def raise_for_status(self): pass
            def json(self): return {"response": "Mocked answer"}
        return MockResponse()

    monkeypatch.setattr("app.main.httpx.AsyncClient.post", mock_post)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/chain/ollama", json={"prompt": "Hello"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"response": "Mocked answer"}