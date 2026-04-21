from fastapi import APIRouter, HTTPException
import requests

from app.settings import settings
from app.analyze.models import LogRequest


MODEL = "qwen2.5:0.5b"

KNOWLEDGE_BASE = {
    "OOMKilled": "Procédure P-042: Augmenter 'resources.limits.memory' de 25%. Vérifier les fuites de mémoire Node.js.",
    "Connection refused": "Procédure P-102: Vérifier le SecurityGroup du RDS et le service K8s endpoint.",
    "504 Gateway Timeout": "Procédure P-088: Vérifier le timeout de l'Ingress Nginx (proxy-read-timeout)."
}

router = APIRouter(
    prefix="/analyze",
)

@router.post("/")
async def analyze_log(request: LogRequest):
    # Mock RAG : On cherche un mot clé simple dans le log
    rag_context = "Aucune procédure spécifique trouvée."
    for key, procedure in KNOWLEDGE_BASE.items():
        if key.lower() in request.content.lower():
            rag_context = procedure
            break

    prompt = (
        f"Tu es un expert SRE. Analyse ce log et réponds UNIQUEMENT en JSON.\n"
        f"DOC RÉFÉRENCE: {rag_context}\n"
        f"LOG: {request.content}"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Format JSON strict: {'statut': 'CRITIQUE'|'WARNING', 'service': 'nom', 'cause': 'raison', 'solution': 'action'}"},
            {"role": "user", "content": prompt}
        ],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 1024}
    }

    try:
        response = requests.post(f"{settings.ollama_url}/chat", json=payload, timeout=15)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"Error calling Ollama API: {e}") # module 'app.settings' has no attribute 'ollama_url'
        raise HTTPException(status_code=500, detail="L'IA est indisponible ou a expiré.")