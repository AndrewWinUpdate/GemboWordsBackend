from pydantic import BaseModel
from typing import Optional

class WordCreate(BaseModel):
    russian: str
    english: str
    transcription: Optional[str]


class WordGet(BaseModel):
    russian: str
    english: str
    transcription: Optional[str]
    id:int
    