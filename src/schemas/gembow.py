from pydantic import BaseModel, Field
from typing import Optional, Union, List
from datetime import datetime
from schemas import admin_wac

class CategoryItemRead(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None
    owner_id: Optional[int] = None
    sort_order: int = 0
    selected: Optional[bool] = False
    
    
class CategorySelect(BaseModel):
    id: int
    
class StartLearnWord(BaseModel):
    id: int
    
    
class Relation_user_word(BaseModel):
    word_id: int
    user_id: int
    state: int = Field(ge=0, le=4) # Union[0, 1, 2, 3, 4] # 0 - not learning, 1 - learning, 2 - learning and problematic, 3 - learned, 4 - already known
    repeat_iteration: Optional[int] = 0
    next_repeat: Optional[datetime] = None
    

class ExampleRepeat(BaseModel):
    russian: str
    english: str
    
    
class CategoryRepeat(BaseModel):
    name: str
    picture: Optional[str]
    sort_order: int

class WordRepeat(BaseModel):
    id: int
    russian: str
    english: str
    transcription: str
    examples: List[ExampleRepeat]
    categories: List[CategoryRepeat]
    
    
    
    

    
class RelationForCategory(BaseModel):
    state: int
    repeat_iteration: Optional[int] = None
    
class SimpleWordGet(BaseModel):
    english: str
    russian: str
    
    
class CategoryItemGet(BaseModel):
    word: SimpleWordGet
    relation: Optional[RelationForCategory] = None
    
class CategoryWithWordsAndStats(BaseModel):
    id: int
    name: str
    words: List[CategoryItemGet]
    
    model_config = {
        "from_attributes": True
    }
    
    
    