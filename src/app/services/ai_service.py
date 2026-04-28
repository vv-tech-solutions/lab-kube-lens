"""Utility for interacting with Qdrant and Ollama embeddings.

This module provides the :class:`AIService` which encapsulates the logic for
embedding log content, querying the knowledge base, and retrieving the best
procedure to apply.
"""

import httpx
from qdrant_client import QdrantClient

from ..settings import settings


class AIService:
    """Service for embedding and querying procedures.

    The service uses Qdrant for vector similarity search and Ollama for text
    embeddings. It exposes two public methods:
    ``get_embedding`` to obtain a vector for a string and ``find_best_procedure``
    to retrieve the most relevant knowledge base entry.
    """

    def __init__(self):
        # Initialise Qdrant client using configuration from settings.
        self.qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        # Endpoint for Ollama embedding model.
        self.ollama_url = f"{settings.ollama_url}/embed"

    def get_embedding(self, text: str, is_query: bool = True) -> list[float]:
        """Return an embedding vector for *text*.

        Parameters
        ----------
        text: str
            The text to embed.
        is_query: bool, optional
            Flag indicating whether the text is a query or a document. The
            prefix used in the prompt changes accordingly.

        Returns
        -------
        list[float]
            The embedding vector returned by Ollama.
        """
        prefix = "search_query: " if is_query else "search_document: "
        technical_hint = "SRE Log Analysis: "
        payload = {
            "model": "nomic-embed-text",
            "input": f"{prefix}{technical_hint}{text}",
        }

        res = httpx.post(self.ollama_url, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()["embeddings"][0]

    def find_best_procedure(self, log_content: str):
        """Find the most relevant procedure for *log_content*.

        The method embeds the log content, queries Qdrant and returns the
        payload of the best matching point. If no point meets the score
        threshold, ``None`` is returned.
        """
        vector = self.get_embedding(f"search_query: {log_content}")

        # 1. Call the new API
        response = self.qdrant.query_points(
            collection_name="sre_knowledge",
            query=vector,
            limit=1,
            score_threshold=0.72,
        )

        # 2. Access the .points attribute which is the actual list
        if not response.points:
            return None

        # 3. Each point is also an object, retrieve its .payload
        best_point = response.points[0]
        return best_point.payload


# Singleton instance used throughout the application.
ai_service = AIService()
