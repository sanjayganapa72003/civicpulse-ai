from typing import Optional

from pydantic import BaseModel


class CitizenRequestCreate(BaseModel):
    text: str
    source: str = "text"

    language: Optional[str] = None

    district: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None