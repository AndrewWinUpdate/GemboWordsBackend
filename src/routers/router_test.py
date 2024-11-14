from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models import User, Category, Word, Example
from sqlalchemy import select
from typing import List
from schemas.User import UserRead
import json
# from schemas.admin_wac import WordCreate
# from typing import List
# from sqlalchemy.orm import Session
# from models import Word

# from database import get_db

router = APIRouter(
    prefix="/test",
    tags=["test"]
)


@router.get("/allusers")
async def allusers(session: AsyncSession = Depends(get_async_session)):
    query = select(User)
    users = await session.execute(query)
    return list(users)[0]


# @router.post("/words_from_big_json")
# async def create_parsed_words_from_reword(session: AsyncSession = Depends(get_async_session)):
#     """
#     dont use
#     """
#     with open("reword_parsed_list.json", "r", encoding="utf-8") as file:
#         data = json.loads(file.read())

#     cats_query = select(Category)
#     result = await session.execute(cats_query)

#     cats = result.scalars().all()

#     cats_map = dict()
#     for i in cats:
#         cats_map[i.name] = i

#     for word in data:
#         new_word = Word(
#             english=word["english"],
#             russian=word["russian"],
#             transcription=word["transcription"]
#         )

#         new_word.categories = [cats_map[c] for c in word["categories"]]
#         if word.get("examples"): new_word.examples = [Example(russian=e["russian"], english=e["english"]) for e in word["examples"]]

#         session.add(new_word)

#     await session.commit()

#     return 0


# @router.get("/drop_all_tables")
# async def drop_all_tables():
#     from models import Base

#     from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
#     from sqlalchemy.future import select

#     engine = create_async_engine("postgresql+asyncpg://myuser:b38n4t34bitb3cb4tc3@localhost/gembowordsdb")

#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

#     return 0


# @router.get("/fix_cats_names_and_imgs")
# async def fix_cats_names_and_imgs(session: AsyncSession = Depends(get_async_session)):
#     old = ["a1", "a2", "b1", "b2", "c1"]
#     new = ["Elementary", "Pre-Intermediate", "Intermediate", "Upper-Intermediate", "Advanced"]


#     for i in range(len(old)):
#         query = select(Category).filter(Category.name==old[i])
#         result = await session.execute(query)
#         cat = result.scalar_one()
#         cat.picture = old[i]
#         cat.name = new[i]

#         await session.commit()

# @router.get("fix_cats_sort_order")
# async def fix_cats_sort_order(session: AsyncSession = Depends(get_async_session)):
#     for i in ["a1", "a2", "b1"]:
#         cat_q = select(Category).filter(Category.name==i)
#         result = await session.execute(cat_q)
#         cat = result.scalar_one()
#         cat.sort_order = -cat.sort_order
#         await session.commit()


# @router.post("/words_from_big_json")
# async def create_parsed_words(session: AsyncSession = Depends(get_async_session)):
#     """
#     dont use
#     """
#     with open("last_list.json", "r", encoding="utf-8") as file:
#         data = json.loads(file.read())

#     cats_query = select(Category)
#     result = await session.execute(cats_query)

#     cats = result.scalars().all()

#     cats_map = dict()
#     for i in cats:
#         cats_map[i.name] = i

#     for word in data:
#         new_word = Word(
#             english=word["english"],
#             russian=word["russian"],
#             transcription=word["transcription"]
#         )

#         new_word.categories = [cats_map[c] for c in word["categories"]]
#         new_word.examples = [Example(russian=e["russian"], english=e["english"]) for e in word["examples"]]

#         session.add(new_word)

#     await session.commit()

#     return 0


# @router.post("/create_my_cats")
# async def create_my_cats(session: AsyncSession = Depends(get_async_session)):
#     # cats = ["a2",
#     # "preposition",
#     # "pronoun",
#     # "b1",
#     # "conjunction",
#     # "verb",
#     # "modal verb",
#     # "b2",
#     # "determiner",
#     # "indefinite article",
#     # "definite article",
#     # "adjective",
#     # "a1",
#     # "number",
#     # "adverb",
#     # "linking verb",
#     # "noun",
#     # "ordinal number",
#     # "exclamation",
#     # "c1",]

#     cats = {
#         "anatomy": "Анатомия",
#         "animals": "Животные",
#         "appearance": "Внешность",
#         "archaeology": "Археология",
#         "architecture": "Архитектура",
#         "art": "Искусство",
#         "basic_verbs": "Базовые глаголы",
#         "business": "Бизнес",
#         "career": "Карьера",
#         "character": "Характер",
#         "clothing": "Одежда",
#         "colors": "Цвета",
#         "computer": "Компьютер",
#         "construction": "Строительство",
#         "ecology": "Экология",
#         "economy": "Экономика",
#         "family": "Семья",
#         "food": "Еда",
#         "furniture": "Мебель",
#         "geography": "География",
#         "health": "Здоровье",
#         "hobby": "Хобби",
#         "home": "Дом, вещи",
#         "idioms": "Идиомы",
#         "irregular_verbs": "Неправильные глаголы",
#         "legal_english": "Юриспруденция",
#         "literature": "Литература",
#         "marketing": "Маркетинг",
#         "mass_media": "СМИ",
#         "math": "Математика",
#         "military_weapons": "Военное дело, оружие",
#         "money": "Деньги",
#         "movie": "Кино",
#         "music": "Музыка",
#         "numbers": "Числительные (колич.)",
#         "numbers_ordinals": "Числительные (порядк.)",
#         "oxford3000_a1": "Oxford 3000 - A1",
#         "oxford3000_a2": "Oxford 3000 - A2",
#         "oxford3000_b1": "Oxford 3000 - B1",
#         "oxford3000_b2": "Oxford 3000 - B2",
#         "oxford5000_b2": "Oxford 5000 - B2",
#         "oxford5000_c1": "Oxford 5000 - C1",
#         "photography": "Фотография",
#         "phrasal_verbs": "Фразовые глаголы",
#         "politics": "Политика",
#         "psychology": "Психология",
#         "signs_of_zodiac": "Знаки зодиака",
#         "space": "Космос",
#         "sport": "Спорт",
#         "time": "Время",
#         "time_days_of_week": "Дни недели",
#         "time_months": "Месяцы",
#         "time_seasons": "Времена года",
#         "top100": "NGSL 1-100",
#         "top1000": "NGSL 101-1000",
#         "top3000": "NGSL 1001-3000",
#         "town": "Город",
#         "transport": "Транспорт",
#         "travel": "Путешествия",
#     }

#     for i in cats:
#         session.add(Category(name=i, name_translated=cats[i]))

#     await session.commit()

#     return 0


# @router.get("/words")
# def get_all_words(db: Session = Depends(get_db)):
#     words = db.query(Word).all()
#     return words  # Возвращаем список объектов Word

# @router.post("/words")
# def get_all_words(words: List[WordCreate], db: Session = Depends(get_db)):


#     for word_data in words:
#         # Создаем объект SQLAlchemy на основе каждого слова
#         new_word = Word(
#             russian=word_data.russian,
#             english=word_data.english,
#             transcription=word_data.transcription,
#         )
#         # Добавляем объект в сессию
#         db.add(new_word)

#     # Сохраняем все изменения в базе данных
#     db.commit()

#     return "all good"
