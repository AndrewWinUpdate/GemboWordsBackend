from sqlalchemy.ext.asyncio import AsyncSession
from models import Word, User, Relation_user_word, Category, Example, LearningState, Stats
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import select, or_, func
from sqlalchemy.orm import joinedload, selectinload
from schemas import gembow as gembow_schemas
from managers.StatsManager import StatsManager


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
        
        stats = await StatsManager.get_stats(user, session)
        
        if stats.last_learn_count >=stats.dayly_goal:
            return HTTPException(status_code=429, detail=f"You have reached your dayly goal ({stats.last_learn_count}/{stats.dayly_goal})")
        
        
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
        
        stats.learning_words += 1
        stats.last_learn_count+=1

        session.add(new_relation)
        await session.commit()
        
        
        if stats.last_learn_count >=stats.dayly_goal:
            return HTTPException(status_code=429, detail=f"You have reached your dayly goal ({stats.last_learn_count}/{stats.dayly_goal})")
        
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
                stats: Stats = await session.get(Stats, user.id)
                
                if relation.state == LearningState.LEARNING_PROBLEMATIC:
                    stats.problematic_words-=1
                    stats.learning_words+=1
                
                if not next_repeat:
                    relation.state = LearningState.LEARNED
                    stats.learning_words-=1
                    stats.learned_words+=1
                    
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
            stats: Stats = await session.get(Stats, user.id)
            stats.learning_words-=1
            stats.problematic_words+=1
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
        stats: Stats = await session.get(Stats, user.id)
        stats.known_words += 1
        session.add(new_relation)
        await session.commit()

        return new_relation

    @staticmethod
    async def get_earliest_next_repeat(user_id: int, session: AsyncSession):
        result = await session.execute(
            select(func.min(Relation_user_word.next_repeat))
            .where(Relation_user_word.user_id == user_id)
        )
        # Получаем минимальное значение next_repeat
        earliest_next_repeat = result.scalar()
        return earliest_next_repeat

    @staticmethod
    async def create_category(category_name, user: User, session: AsyncSession):
        new_category = Category(name=category_name, name_translated=category_name, owner_id=user.id)
        session.add(new_category)
        await session.commit()

        return new_category

    @staticmethod
    async def add_word(word: gembow_schemas.WordCreate, user: User, session: AsyncSession):
        category = await session.get(Category, word.category_id)

        if not category:
            return HTTPException(status_code=404, detail="Target category not found")
        if user.id != category.owner_id:
            return HTTPException(status_code=403, detail="You are not alowed to manage this category")

        new_word: Word = Word(
            english=word.english,
            russian=word.russian,
            transcription=word.transcription,
            owner_id=user.id,
        )
        
        if word.examples:
            new_word.examples = [
                Example(russian=example.russian, english = example.english) for example in word.examples  
            ]
            
        new_word.categories = [category]
        
        session.add(new_word)
        await session.commit()
        
        stmt = select(Word).options(selectinload(Word.examples), selectinload(Word.categories)).filter(Word.id==new_word.id)
    

        result = await session.execute(stmt)

        refreshed_word = result.scalars().first()

        return refreshed_word

