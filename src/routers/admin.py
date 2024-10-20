from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
import schemas.User as user_schemas
from typing import Union, List
import schemas.admin_wac as admin_wac
from managers.AuthManager import get_admin, get_current_user
from models import User, Category, Word, Example
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database import get_async_session
from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload
import json


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/global_categories", response_model=List[admin_wac.CategoryReadWithoutWords])
async def global_categories_read(user=Depends(get_admin), session: AsyncSession = Depends(get_async_session)):
    """
    returns all categories was created by system
    """
    query = select(Category).options(selectinload(Category.words)).filter(Category.owner_id == None)
    
    result = await session.execute(query)
    categories = result.scalars().all()
    return categories



@router.get("/category", response_model=admin_wac.CategoryReadWithWords)
async def category_read(id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(Category).options(joinedload(Category.words).joinedload(Word.examples)).filter(Category.id == id)
    
    result = await session.execute(query)
    cat = result.unique().scalars().one_or_none()
    
    if not cat:
        raise HTTPException(status_code=404, detail=f"Category with id={id} was not found")
    
    return cat

@router.post("/category", response_model=admin_wac.CategoryReadWithoutWords)
async def category_create(category: admin_wac.CategoryCreate, admin=Depends(get_admin), session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Category).values(name = category.name, picture=category.filename).returning(Category)
    
    result = await session.execute(stmt)
    ctg = result.fetchone()[0]
    await session.commit()
    
    
    # print(ctg)
    
    return ctg  
    
    
@router.get("/word", response_model=admin_wac.WordReadWithoutCategories)
async def word_read(id: int):
    ...

@router.post("/word", response_model=admin_wac.WordReadWithCategories)  
async def word_create(word: admin_wac.WordCreate, admin = Depends(get_admin), session: AsyncSession = Depends(get_async_session)):
    new_word = Word(
        english = word.english,
        russian = word.russian,
        transcription = word.transcription,
    )
    print(new_word.id)
    
    
    if word.examples:
        new_word.examples = [
            Example(russian=example.russian, english = example.english) for example in word.examples  
        ]

    session.add(new_word)
    
    
    await session.commit()

    

    stmt = select(Word).options(selectinload(Word.examples), selectinload(Word.categories)).filter(Word.id==new_word.id)
    

    result = await session.execute(stmt)

    refreshed_word = result.scalars().first()

    return refreshed_word
    
    
    


    
@router.get("/words")
async def word_delete(session: AsyncSession = Depends(get_async_session)):
    query = select(Word).options(selectinload(Word.examples), selectinload(Word.categories))
    
    result = await session.execute(query)
    
    words = result.scalars().all()
    return words
    
    
    
    
    
    

    
    
    