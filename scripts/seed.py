import json
import requests
import uuid
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Configuration via ENV pour plus de flexibilité
OLLAMA_URL = os.getenv("OLLAMA_URL", "https://ollama.tailc12aaa.ts.net/api/embed")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
DATA_PATH = "data/knowledge_base.json"

client = QdrantClient(host=QDRANT_HOST, port=6333)

def get_embedding(text):
    payload = {"model": "nomic-embed-text", "input": text}
    res = requests.post(OLLAMA_URL, json=payload)
    res.raise_for_status()
    return res.json()["embeddings"][0]

def run_seed():
    # 1. Charger les données
    with open(DATA_PATH, 'r') as f:
        knowledge_data = json.load(f)

    # 2. Initialiser la collection (Dim 768 pour nomic-embed)
    client.recreate_collection(
        collection_name="sre_knowledge",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

    # 3. Processus d'ingestion
    points = []
    print(f"Starting ingestion of {len(knowledge_data)} procedures...")
    
    for item in knowledge_data:
        vector = get_embedding(item["content"])
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=item
        ))
    
    client.upsert(collection_name="sre_knowledge", points=points)
    print("✅ Ingestion complete. Qdrant is ready.")

if __name__ == "__main__":
    run_seed()