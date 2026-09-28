from pydantic import BaseModel


class DemographicRecord(BaseModel):
    state: str
    district: str
    population: int
    rural_population: int
    urban_population: int
    households: int
    data_year: int
    source: str