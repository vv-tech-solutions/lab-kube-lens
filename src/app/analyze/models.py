"""
Request model for the /analyze endpoint.

The payload contains a single ``content`` field with a maximum length of 1500 characters.
This constraint ensures that the analysis remains responsive and prevents overly large inputs.
"""

from pydantic import BaseModel, Field


class LogRequest(BaseModel):
    """Validate and constrain the log content sent by a client."""
    # Limit to 1500 characters to ensure timely response
    content: str = Field(..., max_length=1500)

