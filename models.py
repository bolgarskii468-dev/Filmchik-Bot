from pydantic import BaseModel
from typing import List, Optional

class Film(BaseModel):
    name: str
    description: str
    rating: float
    genre: str
    year: Optional[str] = ""
    actors: Optional[List[str]] = []
    poster: Optional[str] = ""
    video: str | None = None

