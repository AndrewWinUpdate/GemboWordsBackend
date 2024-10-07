from pydantic import BaseModel, Field
from typing import Optional, List

class Example(BaseModel):
    id: int
    english: str
    russian: str
    owner_id: Optional[int]

class WordReadWithoutCategories(BaseModel):
    id: int
    russian: str
    english: str
    transcription: Optional[str]
    examples = Optional[List[Example]]
    
    
class CategoryReadWithoutWords(BaseModel):
    id: int
    name: str
    picture: Optional[str]
    owner_id: Optional[int]

class CategoryReadWithWords(CategoryReadWithoutWords):
    words: Optional[List[WordReadWithoutCategories]]
    

    
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


class WordReadWithCategories(WordReadWithoutCategories):
    categories: Optional[List[CategoryReadWithoutWords]]
    