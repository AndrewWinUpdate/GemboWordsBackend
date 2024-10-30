from sqlalchemy.ext.asyncio import AsyncSession
from models import Word, User, Relation_user_word, Category, Example, LearningState
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import select, or_, func
from sqlalchemy.orm import joinedload


class LearnManager():

    @staticmethod
    def get_interval(interval_number: int):
        a = [timedelta(hours=1), timedelta(hours=5), timedelta(
            days=1), timedelta(days=5), timedelta(days=20), timedelta(days=60)]
        if isinstance(interval_number, int) and (interval_number >= 0) and (interval_number < len(a)):
            return a[interval_number]
        else:
            return None

    @staticmethod
    def get_next_repeat_time(interval_number: int):
        interval = LearnManager.get_interval(interval_number)
        if not interval:
            return None
        return datetime.now() + interval

    @staticmethod
    async def start_learning(word_id, user: User, session: AsyncSession):
        word = await session.get(Word, word_id)
        if not word:
            return HTTPException(status_code=404, detail="Word not found")
        if not ((word.owner_id == None) or (word.owner_id == user.id)):
            return HTTPException(status_code=403, detail="Forbidden")

        relation = await session.get(Relation_user_word, (word_id, user.id))
        if relation:
            return HTTPException(status_code=409, detail="You are already learning this word")
        new_relation = Relation_user_word(
            word_id=word_id,
            user_id=user.id,
            state=LearningState.LEARNING,
            repeat_iteration=0,
            next_repeat=LearnManager.get_next_repeat_time(0)
        )

        session.add(new_relation)
        await session.commit()

        return new_relation

    @staticmethod
    async def get_words_to_repeat(user: User, session: AsyncSession, time_limited=False):
        current_time = datetime.now()

        query = (
            select(Word)
            .options(joinedload(Word.categories), joinedload(Word.examples))
            .join(Relation_user_word, Relation_user_word.word_id == Word.id)
            .filter(Relation_user_word.user_id == user.id)
            .filter(or_(Relation_user_word.state == 2, Relation_user_word.state == 1))
        )

        if (time_limited):
            query = query.filter(Relation_user_word.next_repeat < current_time)

        result = await session.execute(query)
        words = result.unique().scalars().all()
        return words

    @staticmethod
    async def repeat_word(word_id: int, user: User, session: AsyncSession):
        relation: Relation_user_word = await session.get(Relation_user_word, (word_id, user.id))

        if not relation:
            return HTTPException(status_code=404, detail="relation user-word not found")

        if (relation.state == LearningState.LEARNING) or (relation.state == LearningState.LEARNING_PROBLEMATIC):

            if (relation.next_repeat < datetime.now()):
                relation.repeat_iteration += 1
                next_repeat = LearnManager.get_next_repeat_time(
                    relation.repeat_iteration)
                relation.next_repeat = next_repeat
                if not next_repeat:
                    relation.state = LearningState.LEARNED
                await session.commit()
                return relation
            else:
                return relation
        else:
            return HTTPException(status_code=409, detail="You can't repeat this word")

    @staticmethod
    async def forget_word(word_id: int, user: User, session: AsyncSession):
        relation: Relation_user_word = await session.get(Relation_user_word, (word_id, user.id))

        if not relation:
            return HTTPException(status_code=404, detail="relation user-word not found")

        if (relation.state == LearningState.LEARNING) or (relation.state == LearningState.LEARNING_PROBLEMATIC) or (relation.state == LearningState.LEARNED):

            relation.repeat_iteration = min(relation.repeat_iteration, 3)
            next_repeat = LearnManager.get_next_repeat_time(
                relation.repeat_iteration)
            relation.next_repeat = next_repeat
            relation.state = LearningState.LEARNING_PROBLEMATIC
            await session.commit()
            return relation
        else:
            return HTTPException(status_code=409, detail="You can't repeat this word")

    @staticmethod
    async def already_know(word_id: int, user: User, session: AsyncSession):
        relation: Relation_user_word = await session.get(Relation_user_word, (word_id, user.id))

        if relation:
            return HTTPException(status_code=409, detail="This word is not new")

        new_relation = Relation_user_word(
            word_id=word_id,
            user_id=user.id,
            state=4,
            repeat_iteration=0,
            next_repeat=None
        )

        session.add(new_relation)
        await session.commit()

        return new_relation
    
    
    @staticmethod
    async def get_earliest_next_repeat(user_id: int, session: AsyncSession):
        result = await session.execute(
            select(func.min(Relation_user_word.next_repeat))
            .where(Relation_user_word.user_id == user_id)
        )
        earliest_next_repeat = result.scalar()  # Получаем минимальное значение next_repeat
        return earliest_next_repeat

    