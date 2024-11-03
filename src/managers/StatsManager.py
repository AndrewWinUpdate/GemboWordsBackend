from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models import User, Stats, Relation_user_word
from managers.AuthManager import get_current_user
from schemas import stats as stats_scheme
from datetime import date
from sqlalchemy import select

class StatsManager():
    
    @staticmethod
    def update_dayly_stats(stats: Stats) -> Stats:
        today = date.today()
        
        # print(today, stats.last_day_learned, stats.last_day_learned==today)
        
        if today == stats.last_day_learned:
            return stats
        
        stats.last_day_learned = today
        stats.last_learn_count = 0
        
        return stats
    
    @staticmethod
    async def recount_stats(user: User, session: AsyncSession):
        stats = session.get(Stats, user.id)
        
        stats = StatsManager.update_dayly_stats()
        
        stats.learned_words = 0
        stats.learning_words = 0
        stats.known_words = 0
        stats.problematic_words = 0
        
        relations_get_query = select(Relation_user_word).filter(Relation_user_word.user_id==user.id)
        
        result = await session.execute(relations_get_query)
        
        relations = result.scalars().all()
        
        for rel in relations:
            if rel.state == 3: stats.learned_words += 1
            if rel.state == 1: stats.learning_words += 1
            if rel.state == 4: stats.known_words += 1
            if rel.state == 2: stats.problematic_words += 1
            
        await session.commit()
        
        return True
    
    @staticmethod
    async def alowed_learn(user: User, session: AsyncSession):
        stats: Stats = await session.get(Stats, user.id)
        
        new_stats: Stats = StatsManager.update_dayly_stats(stats)
        
        if stats.last_day_learned!=new_stats.last_day_learned:
            stats.last_day_learned = new_stats.last_day_learned
            stats.last_learn_count = new_stats.last_learn_count
            await session.commit()
            
        if stats.last_learn_count < stats.dayly_goal:return stats
        else: return False
        
        
    @staticmethod
    async def get_stats(user: User, session: AsyncSession):
        stats: Stats = await session.get(Stats, user.id)
        
        temp_day = stats.last_day_learned
        stats: Stats = StatsManager.update_dayly_stats(stats)
        
        if stats.last_day_learned!=temp_day:
            
            print("999999999999999999999999999999999")
            
            print(stats.last_day_learned, stats.last_learn_count)
            await session.commit()
            
        else:
            print(121233333333333333333333333333333333)
            print(stats.last_day_learned, stats.last_learn_count)
            
            
        
        return stats