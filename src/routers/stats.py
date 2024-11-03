from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models import User, Stats
from managers.AuthManager import get_current_user
from schemas import stats as stats_scheme

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)


@router.get("/", response_model=stats_scheme.StatsRead)
async def get_stats(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    stats = await session.get(Stats, user.id)
    return stats