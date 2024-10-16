from fastapi import APIRouter, Depends, HTTPException
import schemas.User as user_schemas
from typing import Union
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from managers.AuthManager import AuthManager


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register")  #, response_model=Union[user_schemas.RegisterSuccessResponse, user_schemas.RegisterErrorResponse]
async def register(data: user_schemas.RegisterInput, session: AsyncSession = Depends(get_async_session)):
    
    result = await AuthManager.create_user(data, session)
    if isinstance(result, HTTPException):
        raise result
    
    return result
    
@router.post("/login") #, response_model=Union[user_schemas.LoginSuccessResponse, user_schemas.LoginErrorResponse]
async def login(data: user_schemas.LoginInput, session: AsyncSession = Depends(get_async_session)):
    result = await AuthManager.login(data, session)
    
    if isinstance(result, HTTPException):
        raise result
    
    return result
        
    
    
@router.get("/whoami", response_model = Union[user_schemas.UserRead, user_schemas.UnauthorizedError])
async def whoami(token: str, session: AsyncSession = Depends(get_async_session)):
    res = await AuthManager.whoami(token, session)
    return res