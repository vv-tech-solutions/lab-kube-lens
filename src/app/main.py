"""Main entry point for the FastAPI application.

The module configures the FastAPI instance, applies CORS middleware, exposes a health‑check endpoint and mounts the analyze router.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .analyze.router import router as analyze_router

# Application instance with a descriptive title
app = FastAPI(title="V&V Tech AIOps Lab")

# Configure CORS to allow local front‑end development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health‑check endpoint for monitoring and CI health checks
@app.get("/health")
async def health():
    return {"status": "OK"}
# Mount the analysis routes under /analyze
app.include_router(analyze_router)
