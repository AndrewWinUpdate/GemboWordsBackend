from fastapi import APIRouter
import schemas.User as user_schemas
from typing import Union


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=Union[user_schemas.RegisterSuccessResponse, user_schemas.RegisterErrorResponse])
async def register(data: user_schemas.RegisterInput):
    ...
    
@router.post("/login", response_model=Union[user_schemas.LoginSuccessResponse, user_schemas.LoginErrorResponse])
async def login(data: user_schemas.LoginInput):
    ...
    
@router.get("/whoami", response_model = user_schemas.UserRead)
async def whoami():
    ...