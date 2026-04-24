# 🔍 KubeLens

KubeLens is an AI-powered Kubernetes log analysis and monitoring API. It leverages a Retrieval-Augmented Generation (RAG) engine to identify cluster anomalies and suggest remediations based on your specific log history.

## 🚀 Key Features
- **ARM64 Native**: Optimized for ARM-based infrastructure (Scaleway Kapsule AMP2 nodes).
- **RAG Engine**: Vector indexing via Qdrant and LLM analysis via Ollama.
- **Secure by Design**: Integrated with Kubernetes External Secrets (ESO) for credential management and Zot OCI Registry for secure image storage.
- **Modern Structure**: Follows the `src-layout` standard and PEP 621 (`pyproject.toml`).

## 🛠 Quick Start

### Local Development
```bash
# Install in editable mode with dev tools
pip install -e ".[dev]"

# Set the source path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run the server
python -m app.server
```

### Build for Production (ARM64)

```bash
# Build using Buildah on an ARM-compatible runner
buildah build --arch arm64 -t oci.vvtechsolutions.eu/kube-lens:latest .
```

## 🏗 Technical Stack

- Backend: FastAPI, Pydantic v2
- Vector Database: Qdrant
- LLM Integration: LangChain / Ollama
- Infrastructure: Kubernetes (Scaleway Kapsule ARM)
- CI/CD: GitLab CI + Buildah (with QEMU emulation for cross-platform building)