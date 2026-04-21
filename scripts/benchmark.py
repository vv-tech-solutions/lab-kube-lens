import requests
import time

OLLAMA_URL = "https://ollama.tailc12aaa.ts.net/api/chat"
MODEL = "qwen2.5:0.5b"

# Log massif pour tester la synthèse
LONG_LOG = """2026-04-16T14:02:01.452Z [node-app-7d4f9] INFO: Incoming request GET /api/v1/inventory
2026-04-16T14:02:05.110Z [node-app-7d4f9] WARN: Memory usage at 89% (heap_limit reached)
2026-04-16T14:02:08.891Z [node-app-7d4f9] ERROR: Fatal error in V8: Scavenger: semi-space copy, Allocation failed - process out of memory
2026-04-16T14:02:09.100Z [k8s-system] EVENT: Pod node-app-7d4f9 container "api" terminated with exit code 137 (OOMKilled)
2026-04-16T14:02:10.500Z [k8s-system] INFO: Restarting container "api" in pod node-app-7d4f9...
2026-04-16T14:02:15.221Z [node-app-7d4f9] INFO: Application starting up (version 2.4.1)...
2026-04-16T14:02:16.890Z [node-app-7d4f9] ERROR: DB_CONNECTION_TIMEOUT: Unable to reach database "prod-db-cluster" at 10.0.45.12:5432
2026-04-16T14:02:16.891Z [node-app-7d4f9] ERROR: Connection pool exhausted while waiting for database response.
2026-04-16T14:02:20.005Z [k8s-system] WARN: Liveness probe failed for pod node-app-7d4f9: HTTP 503 Service Unavailable
2026-04-16T14:02:25.110Z [k8s-system] ERROR: Readiness probe failed: Pod is not ready to accept traffic.
2026-04-16T14:02:30.450Z [ingress-nginx] INFO: 192.168.1.45 - - [16/Apr/2026:14:02:30 +0000] "GET /api/v1/inventory" 504 Gateway Timeout
2026-04-16T14:02:32.000Z [k8s-system] EVENT: Pod node-app-7d4f9 status changed to CrashLoopBackOff."""

def test_heavy_log():
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "Tu es un expert SRE. Analyse le log et réponds UNIQUEMENT en JSON: {'statut': 'CRITIQUE'|'WARNING', 'service': 'nom', 'cause': 'raison courte', 'solution': 'action'}"
            },
            {"role": "user", "content": LONG_LOG}
        ],
        "format": "json", # On force le format JSON via Ollama
        "stream": False,
        "options": {"temperature": 0}
    }

    start = time.time()
    response = requests.post(OLLAMA_URL, json=payload)
    print(f"--- ANALYSE LOG RÉEL ---\n{response.json()['message']['content']}")
    print(f"⏱️ Temps : {time.time()-start:.2f}s")

if __name__ == "__main__":
    test_heavy_log()