from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    state: str = "Karnataka"
    district: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None


class CitizenRequest(BaseModel):
    raw_text: str

    language: str
    category: str
    issue_type: str

    location: Location

    severity: int = Field(ge=1, le=5)

    source: str = "text"

    created_at: datetime