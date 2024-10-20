import jwt
from random import randint
from models import User
from schemas.User import RegisterInput, LoginInput, UserRead, UnauthorizedError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi import Depends, Request, Response, HTTPException
from database import get_async_session
from sqlalchemy import select
import bcrypt
from fastapi import HTTPException, Request

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, TOKEN_NAME


class UnauthorizedException(BaseException):
    ...


class AuthManager():
    

    
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)  # По умолчанию 15 минут
        to_encode.update({"exp": expire})  # Добавляем время истечения
        print(to_encode, SECRET_KEY, ALGORITHM)
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("email")
            return email
        except Exception:
            return None
        
    
    
        
        
    
    @staticmethod
    async def is_email_exists(email: str, session: AsyncSession):
        user = await session.query(User).filter_by(email=email).first()
        return user
        
    @staticmethod
    async def get_by_email(email: str, session: AsyncSession):
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalars().first()
        
    def hash_password(password: str) -> str:
        # Генерируем соль
        salt = bcrypt.gensalt()
        # Хешируем пароль с солью
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    
    def check_password(plain_password: str, hashed_password: str) -> bool:
    # Сравниваем введённый пароль с хешированным
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    
    @staticmethod
    async def create_user(user: RegisterInput, session: AsyncSession):
        exists = await AuthManager.get_by_email(user.email, session)
        print(exists)
        if exists:
            print("exists")
            return HTTPException(status_code=409, detail="User with such email is already registered")
        new_user = User(email=user.email, 
                        hashed_password=AuthManager.hash_password(user.password),
                        
                        )
        
        session.add(new_user)
        await session.commit()
        
        return new_user
    

            
        
    # @staticmethod
    # def setJWT(user: User, response: Response):
    #     print(ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY)
    #     data = {
    #         "email": user.email
    #     }
    #     token = UserManager.create_access_token(data)
    #     response.set_cookie(TOKEN_NAME, token)
        
        
        
        
        
        
    @staticmethod
    def auth_jwt(token: str):
        email = AuthManager.verify_token(token)
        return email
    
    
    
    @staticmethod
    async def get_current_user(request: Request, session: AsyncSession = Depends(get_async_session)) -> User:
        email = AuthManager.verify_token(request.cookies.get(TOKEN_NAME))
        if not email:
            raise UnauthorizedException
        
        user = await AuthManager.get_by_email(email, session)
        if not user:
            raise UnauthorizedException
        return user
    
    @staticmethod
    def logout(response: Response):
        response.set_cookie(TOKEN_NAME, "")
        
        
        
    @staticmethod
    async def login(data: LoginInput, session: AsyncSession):
        query = select(User).filter(User.email == data.email)
        result = await session.execute(query)
        user = result.scalar()
        
        if user:
            pass_checked = AuthManager.check_password(data.password, user.hashed_password)
            if pass_checked:
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = AuthManager.create_access_token(
                    data={"email": data.email},  # subject (sub) обычно содержит уникальный идентификатор пользователя
                    expires_delta=access_token_expires
                )
                
                return {"token": access_token, "token_type": "bearer"}
            else:
                return HTTPException(status_code=401, detail="Incorrect email or password")
        else:
            return HTTPException(status_code=401, detail="Incorrect email or password")
        
        
        
    @staticmethod
    async def whoami(token: str, session: AsyncSession):
        email = AuthManager.auth_jwt(token)
        print(f"email: {email}")
        if not email:
            return UnauthorizedError(msg = "Unauthorized")
        else:
            query = select(User).filter(User.email == email)
            result = await session.execute(query)
            user = result.scalar()
            return user
        
        

async def get_current_user(request: Request, session: AsyncSession = Depends(get_async_session)):
    token = request.cookies.get("jwt")
    
    user = await AuthManager.whoami(token, session)
    if isinstance(user, User):
        return user
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

async def get_admin(user=Depends(get_current_user)):
    if (user.is_admin):
        return user
    else:
        raise HTTPException(403, "Forbidden")