from pydantic import BaseModel, Field

class LogRequest(BaseModel):
    # On limite à 1500 caractères pour le temps de réponse
    content: str = Field(..., max_length=1500)
