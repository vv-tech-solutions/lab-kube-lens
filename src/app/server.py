"""
Server entry point for running the FastAPI application with Uvicorn.

When executed directly, the script launches Uvicorn in reload mode,
making it convenient for local development.
"""

import uvicorn
from .main import app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
