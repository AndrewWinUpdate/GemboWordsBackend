from fastapi import APIRouter, Depends, HTTPException
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from managers.AuthManager import get_current_user
from models import User, Category, Word, word_category_association, Relation_user_word
import schemas.gembow as gembow_schema
from typing import List
from sqlalchemy import select, func, or_, and_
from schemas import admin_wac
from sqlalchemy.orm import joinedload, aliased
from managers.LearnManager import LearnManager
from managers.StatsManager import StatsManager
from datetime import datetime


router = APIRouter(
    prefix="/gembow",
    tags=["gembow"]
)


@router.get("/get_categories", response_model=List[gembow_schema.CategoryItemRead])
async def get_categories(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    global_categories_query = select(
        Category).filter(or_(Category.owner_id == None, Category.owner_id==user.id))
    global_categories_query_result = await session.execute(global_categories_query)
    global_categories = global_categories_query_result.scalars().all()

    user_selected_categories = user.categories

    for j in range(len(user_selected_categories)):
        for i in range(len(global_categories)):
            if global_categories[i].id == user_selected_categories[j].id:
                global_categories[i].selected = True
                break

    return global_categories


@router.post("/select_category", response_model=gembow_schema.CategoryItemRead)
async def select_category(category_select: gembow_schema.CategorySelect, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):

    category_id = category_select.id
    category = await session.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with id={category_id} was not found")
    if (category.owner_id != None and category.owner_id != user.id):
        raise HTTPException(
            status_code=403, detail=f"You dont have an access to this category")
    if category in user.categories:
        category.selected = True
        return category
    user.categories.append(category)

    await session.commit()

    category.selected = True
    return category


@router.post("/unselect_category", response_model=gembow_schema.CategoryItemRead)
async def unselect_category(category_select: gembow_schema.CategorySelect, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):

    category_id = category_select.id
    category = await session.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with id={category_id} was not found")
    if (category.owner_id != None and category.owner_id != user.id):
        raise HTTPException(
            status_code=403, detail=f"You dont have an access to this category")
    if not (category in user.categories):
        return category
    user.categories.remove(category)

    await session.commit()

    return category


@router.get("/get_new_words", response_model=List[admin_wac.WordReadWithCategories])
async def get_new_words(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    
    stats = await StatsManager.get_stats(user, session)
        
    if stats.last_learn_count >=stats.dayly_goal:
        raise HTTPException(status_code=429, detail=f"You have reached your dayly goal ({stats.last_learn_count}/{stats.dayly_goal})")
    
    
    RelationUserWordAlias = aliased(Relation_user_word)

    query = (
        select(Word)
        .options(joinedload(Word.categories), joinedload(Word.examples))
        .outerjoin(
            RelationUserWordAlias,
            and_(
                RelationUserWordAlias.word_id == Word.id,
                # предполагается, что user — текущий пользователь
                RelationUserWordAlias.user_id == user.id
            )
        )
        .filter(
            or_(
                RelationUserWordAlias.word_id == None,  # связь отсутствует
                RelationUserWordAlias.state == 0        # либо state равен 0
            )
        )
        .filter(Word.categories.any(Category.id.in_([category.id for category in user.categories])))
        .order_by(func.random())
        .limit(5)
    )
    result = await session.execute(query)

    words = result.unique().scalars().all()

    return words


@router.post("/start_learn_word" , response_model=gembow_schema.Relation_user_word) 
async def start_learn_word(word_to_learn: gembow_schema.StartLearnWord, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):

    relation = await LearnManager.start_learning(word_to_learn.id, user, session)

    
    print(relation, type(relation), isinstance(relation, HTTPException))
    
    if isinstance(relation, HTTPException):
        raise relation
    
    return relation


@router.get("/repeat/time_limited", response_model=List[gembow_schema.WordRepeat])
async def get_words_to_repeat(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    words = await LearnManager.get_words_to_repeat(user, session, True)
    return words


@router.get("/repeat", response_model=List[gembow_schema.WordRepeat])
async def get_words_to_repeat(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    words = await LearnManager.get_words_to_repeat(user, session)
    return words


@router.post("/repeat", response_model=gembow_schema.Relation_user_word)
async def repeat_word(word: gembow_schema.StartLearnWord, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await LearnManager.repeat_word(word.id, user, session)

    if isinstance(result, HTTPException):
        raise result

    return result


@router.post("/forget", response_model=gembow_schema.Relation_user_word)
async def forget_word(word: gembow_schema.StartLearnWord, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await LearnManager.forget_word(word.id, user, session)

    if isinstance(result, HTTPException):
        raise result

    else:
        return result


@router.post("/already_know", response_model=gembow_schema.Relation_user_word)
async def already_know(word: gembow_schema.StartLearnWord, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await LearnManager.already_know(word.id, user, session)

    if isinstance(result, HTTPException):
        raise result

    else:
        return result


@router.get("/category/{category_id}", response_model=gembow_schema.CategoryWithWordsAndStats)
async def get_words_with_relations(
    category_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Получаем категорию
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Подзапрос для получения слов, связанных с категорией
    subquery = (
        select(word_category_association.c.word_id)
        .where(word_category_association.c.category_id == category_id)
        .subquery()
    )

    # Алиас для ассоциации Relation_user_word
    relation_alias = aliased(Relation_user_word)

    # Основной запрос для получения слов и их связей с пользователем
    query = (
        select(Word, relation_alias)
        .outerjoin(
            relation_alias,
            (relation_alias.word_id == Word.id) & (
                relation_alias.user_id == user.id)
        )
        .where(Word.id.in_(subquery))
    )

    # Выполняем запрос и измеряем время выполнения
    start_time = datetime.now()
    result = await session.execute(query)
    print(datetime.now() - start_time)

    # Обрабатываем результаты и собираем их в нужный формат
    words_with_relations = [
        gembow_schema.CategoryItemGet(
            word=gembow_schema.SimpleWordGet(
                id=word.id,
                english=word.english,
                russian=word.russian
            ),
            relation=gembow_schema.RelationForCategory(
                state=relation.state,
                repeat_iteration=relation.repeat_iteration
            ) if relation else None
        )
        for word, relation in result.unique().all()
    ]

    # Возвращаем категорию с включёнными словами и отношениями
    return gembow_schema.CategoryWithWordsAndStats(
        id=category.id,
        name=category.name,
        name_translated=category.name_translated,
        words=words_with_relations,
        owner_id=category.owner_id
    )


@router.get("/earliest_repeat")
async def get_earlist_repeat_time(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await LearnManager.get_earliest_next_repeat(user.id, session)
    return result


@router.post("/create_category", response_model=gembow_schema.CategoryReadWithoutWords)
async def create_category(category: gembow_schema.CategoryCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await LearnManager.create_category(category.name, user, session)
    
    if isinstance(result, HTTPException):
        raise HTTPException
    else:
        return result
    
    
@router.post("/add_word", response_model=gembow_schema.WordRepeat)
async def add_word_to_custom_category(word: gembow_schema.WordCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await LearnManager.add_word(word, user, session)
    
    if isinstance(result, HTTPException):
        raise result
    else:
        return result
    
    
@router.delete("/word")
async def delete_word(word: gembow_schema.StartLearnWord, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    w = await session.get(Word, word.id)
    if not w:
        raise HTTPException(status_code=404, detail="Word not found")
    if w.owner_id != user.id:
        print(w.owner_id, user.id)
        raise HTTPException(status_code=403, detail="You cannot delete this word")

    await session.delete(w)
    await session.commit()
    
    return 1