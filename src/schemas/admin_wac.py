from pydantic import BaseModel, Field
from typing import Optional, List

class ExampleRead(BaseModel):
    id: int
    english: str
    russian: str
    owner_id: Optional[int] = None
    
class ExampleCreate(BaseModel):
    english: str
    russian: str
    owner_id: Optional[int] = None

class WordReadWithoutCategories(BaseModel):
    id: int
    russian: str
    english: str
    transcription: Optional[str] = ""
    examples: Optional[List[ExampleRead]] = []
    
    
class CategoryReadWithoutWords(BaseModel):
    id: int
    name: str
    picture: Optional[str]
    owner_id: Optional[int]
    sort_order: int
    
class CategoryCreate(BaseModel):
    name: str
    filename: Optional[str] = None

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
    categories: Optional[List[int]] = None
    
    examples: Optional[List[ExampleCreate]] = None
    
    
class WordUpdate(BaseModel):
    russian: str
    english: str
    transcription: Optional[str]
    categories: List[int]


class WordReadWithCategories(WordReadWithoutCategories):
    categories: Optional[List[CategoryReadWithoutWords]] = []
    