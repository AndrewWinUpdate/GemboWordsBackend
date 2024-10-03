from pydantic import BaseModel



class Stats(BaseModel):
    learned_words: int
    learning_words: int
    known_words: int
    problematic_words: int
