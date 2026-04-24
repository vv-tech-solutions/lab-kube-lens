import requests
from qdrant_client import QdrantClient
from ..settings import settings

class AIService:
    def __init__(self):
        self.qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        self.ollama_url = f"{settings.ollama_url}/embed"

    def get_embedding(self, text: str, is_query: bool = True) -> list[float]:
        prefix = "search_query: " if is_query else "search_document: "
        technical_hint = "SRE Log Analysis: "
        payload = {
            "model": "nomic-embed-text", 
            "input": f"{prefix}{technical_hint}{text}"
        }
        
        res = requests.post(self.ollama_url, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()["embeddings"][0]
    
    def find_best_procedure(self, log_content: str):
        vector = self.get_embedding(f"search_query: {log_content}")
        
        # 1. Appel à la nouvelle API
        response = self.qdrant.query_points(
            collection_name="sre_knowledge",
            query=vector,
            limit=1,
            score_threshold=0.72
        )
        
        # 2. On accède à l'attribut .points qui est la liste réelle
        if not response.points:
            return None
            
        # 3. Chaque point est aussi un objet, on récupère son .payload
        best_point = response.points[0]
        return best_point.payload
    
ai_service = AIService()