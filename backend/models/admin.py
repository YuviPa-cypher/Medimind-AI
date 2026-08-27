from pydantic import BaseModel, Field

class DomainRequest(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)
