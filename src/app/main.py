from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .analyze.router import router as analyze_router

app = FastAPI(title="V&V Tech AIOps Lab")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health‑check endpoint
@app.get("/health")
async def health():
    return {"status": "OK"}

app.include_router(analyze_router)
