from pydantic import BaseModel, Field
from typing import Optional, List

class WordReadWithoutCategories(BaseModel):
    id: int
    russian: str
    english: str
    transcription: Optional[str]

class CategoryReadWithWords(BaseModel):
    id: int
    name: str
    picture: Optional[str]
    owner_id: Optional[int]
    
    words: Optional[List[WordReadWithoutCategories]]
    

class CategoryReadWithoutWords(BaseModel):
    id: int
    name: str
    picture: Optional[str]
    owner_id: Optional[int]
    
    
    
class CategoryUpdate(BaseModel):
    id: int
    name: str
    picture: Optional[str]
    owner_id: Optional[int]
    
    
    
class WordCreate(BaseModel):
    russian: str
    english: str
    transcription: Optional[str]
    categories: List[int]
    
    
class WordUpdate(BaseModel):
    russian: str
    english: str
    transcription: Optional[str]
    categories: List[int]


class WordReadWithCategories(BaseModel):
    id: int
    russian: str
    english: str
    transcription: Optional[str]
    categories: Optional[List[CategoryReadWithoutWords]]
    
