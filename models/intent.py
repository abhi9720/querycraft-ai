from pydantic import BaseModel

class Intent(BaseModel):
    intent: str
