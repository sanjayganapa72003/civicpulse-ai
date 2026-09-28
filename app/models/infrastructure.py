from typing import Any

from pydantic import BaseModel


class InfrastructureRecord(BaseModel):
    state: str
    district: str
    category: str
    indicators: dict[str, Any]
    data_year: int
    source: str
    source_url: str