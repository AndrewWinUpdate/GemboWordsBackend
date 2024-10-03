from fastapi import APIRouter, Depends
from schemas.words import WordCreate
from typing import List
from sqlalchemy.orm import Session
from models import Word

from database import get_db

router = APIRouter(
    prefix="/test",
    tags=["test"]
)

@router.get("/words")
def get_all_words(db: Session = Depends(get_db)):
    words = db.query(Word).all()
    return words  # Возвращаем список объектов Word

@router.post("/words")
def get_all_words(words: List[WordCreate], db: Session = Depends(get_db)):
    
    
    for word_data in words:
        # Создаем объект SQLAlchemy на основе каждого слова
        new_word = Word(
            russian=word_data.russian,
            english=word_data.english,
            transcription=word_data.transcription,
        )
        # Добавляем объект в сессию
        db.add(new_word)
    
    # Сохраняем все изменения в базе данных
    db.commit()
    
    return "all good"