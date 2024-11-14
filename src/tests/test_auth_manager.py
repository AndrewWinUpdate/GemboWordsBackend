import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import timedelta, datetime
import jwt
from config import *
from managers.AuthManager import AuthManager, UnauthorizedException, get_current_user, get_admin
from schemas.User import RegisterInput
from models import User, Stats
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
import asyncio
from fastapi import HTTPException

# Константы для тестов
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"
TEST_HASHED_PASSWORD = AuthManager.hash_password(TEST_PASSWORD)

# Тестируем метод create_access_token
def test_create_access_token():
    data = {"email": TEST_EMAIL}
    expires = timedelta(minutes=5)
    token = AuthManager.create_access_token(data, expires)
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["email"] == TEST_EMAIL
    assert "exp" in decoded_data

# Тестируем метод verify_token
def test_verify_token():
    # Создаем действительный токен
    data = {"email": TEST_EMAIL}
    token = AuthManager.create_access_token(data, timedelta(minutes=5))
    email = AuthManager.verify_token(token)
    assert email == TEST_EMAIL

    # Проверка недействительного токена
    invalid_token = "invalid.token.value"
    assert AuthManager.verify_token(invalid_token) is None

# Тесты для hash_password и check_password
def test_hash_password():
    hashed = AuthManager.hash_password(TEST_PASSWORD)
    assert bcrypt.checkpw(TEST_PASSWORD.encode('utf-8'), hashed.encode('utf-8'))

def test_check_password():
    assert AuthManager.check_password(TEST_PASSWORD, TEST_HASHED_PASSWORD)
    assert not AuthManager.check_password("wrong_password", TEST_HASHED_PASSWORD)

@pytest.mark.asyncio
async def test_is_email_exists_exists():
    # Мок для сессии и методов запроса
    mock_session = MagicMock()
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter_by.return_value
    mock_filter.first = AsyncMock(return_value=User(email="test@example.com"))

    # Вставляем мок в тестируемую функцию
    user = await AuthManager.is_email_exists("test@example.com", mock_session)

    # Проверяем, что возвращаемый объект правильный
    assert user is not None
    assert user.email == "test@example.com"
    
    
@pytest.mark.asyncio
async def test_is_email_exists_not_exists():
    # Мок для сессии и методов запроса
    mock_session = MagicMock()
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter_by.return_value
    mock_filter.first = AsyncMock(return_value=None)

    # Вставляем мок в тестируемую функцию
    user = await AuthManager.is_email_exists("test@example_not_exist.com", mock_session)

    # Проверяем, что возвращаемый объект правильный
    assert user == None
    
    
@pytest.mark.asyncio
async def test_get_by_email():
    mock_session = MagicMock()
    
    email = "test@example.com"
    
    session_execute_result = MagicMock()
    session_execute_result.scalars.return_value.first = MagicMock(return_value=User(email="test@example.com"))
    
    mock_session.execute = AsyncMock(return_value=session_execute_result)
    
    user = await AuthManager.get_by_email(email, mock_session)
    
    
    assert user is not None
    assert user.email == email
    



@pytest.mark.asyncio
async def test_create_user():
    # Подготовка данных для теста
    test_user = RegisterInput(email=TEST_EMAIL, password="password")
    
    # Создаем сессию мока
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Мокаем результат AuthManager.get_by_email так, чтобы он возвращал None,
    # имитируя отсутствие пользователя с указанным email
    with patch("managers.AuthManager.AuthManager.get_by_email", new=AsyncMock(return_value=None)):
        
        # Проверяем случай, когда пользователя нет, и создается новый пользователь
        result = await AuthManager.create_user(test_user, mock_session)
        
        # Проверяем, что не было поднято исключение и новый пользователь добавлен в сессию
        assert mock_session.add.call_count == 2
        assert mock_session.commit.called
        assert result is not None
        assert result.email == TEST_EMAIL
        

    # Теперь протестируем случай, когда пользователь уже существует
    with patch("managers.AuthManager.AuthManager.get_by_email", new=AsyncMock(return_value=True)):
        
        result = await AuthManager.create_user(test_user, mock_session)
        
        assert isinstance(result, HTTPException)
        assert result.status_code == 409
        assert result.detail == "User with such email is already registered"
        
        

def test_auth_jwt_valid():
    
    valid_token = AuthManager.create_access_token(data={"email": TEST_EMAIL})
    
    email = AuthManager.auth_jwt(valid_token)
    
    assert email == TEST_EMAIL
    
    
def test_auth_jwt_invalid():
    
    invalid_token = "34tv678345v678b345v678bn345v678n345v678n345v678n 345v789n345v7890jm345v789nm"

    email = AuthManager.auth_jwt(invalid_token)
    assert email == None


def test_auth_jwt_expired():
    
    expired_token = AuthManager.create_access_token(data={"email": TEST_EMAIL}, expires_delta=timedelta(days=-5))
    
    email = AuthManager.auth_jwt(expired_token)
    assert email == None
    
    
    

@pytest.mark.asyncio
async def test_get_current_user_valid():
    request = MagicMock()
    request.cookies = {TOKEN_NAME: AuthManager.create_access_token(data={"email": TEST_EMAIL})}
    session = MagicMock()
    
    with patch("managers.AuthManager.AuthManager.get_by_email", new=AsyncMock(return_value=User(email=TEST_EMAIL))):
        result = await AuthManager.get_current_user(request, session)
        
        assert isinstance(result, User)
        
        assert result.email == TEST_EMAIL
        
        
        
@pytest.mark.asyncio
async def test_get_current_user_unath():
    request = MagicMock()
    request.cookies = {TOKEN_NAME: AuthManager.create_access_token(data={"email": TEST_EMAIL})}
    session = MagicMock()
    
    with patch("managers.AuthManager.AuthManager.get_by_email", new=AsyncMock(return_value=None)):
        
        
        with pytest.raises(UnauthorizedException) as exc_info:
            result = await AuthManager.get_current_user(request, session)
            
            
@pytest.mark.asyncio
async def test_get_current_user_fake():
    request = MagicMock()
    request.cookies = {TOKEN_NAME: AuthManager.create_access_token(data={"emaill": TEST_EMAIL})}
    session = MagicMock()
    
    with patch("managers.AuthManager.AuthManager.get_by_email", new=AsyncMock(return_value=None)):
        
        
        with pytest.raises(UnauthorizedException) as exc_info:
            result = await AuthManager.get_current_user(request, session)
    
    
    
def test_logout():
    response = MagicMock()
    
    AuthManager.logout(response)
    
    response.set_cookie.assert_called_once()
    

@pytest.mark.asyncio
async def test_login_valid():
    login_data = MagicMock(
        email= TEST_EMAIL,
        password = TEST_PASSWORD
    )
    session = MagicMock()
    
    session_execute_result = MagicMock()
    
    session_execute_result.scalar.return_value = User(email=TEST_EMAIL, hashed_password=TEST_HASHED_PASSWORD)
    
    session.execute = AsyncMock(return_value=session_execute_result)
    
    result = await AuthManager.login(login_data, session)
    
    assert isinstance(result, dict)
    assert result.get("token")
    
    
@pytest.mark.asyncio
async def test_login_wrong_pass():
    login_data = MagicMock(
        email= TEST_EMAIL,
        password = TEST_PASSWORD + "123"
    )
    session = MagicMock()
    
    session_execute_result = MagicMock()
    
    session_execute_result.scalar.return_value = User(email=TEST_EMAIL, hashed_password=TEST_HASHED_PASSWORD)
    
    session.execute = AsyncMock(return_value=session_execute_result)
    
    result: HTTPException = await AuthManager.login(login_data, session)
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 401
    assert result.detail == "Incorrect email or password"
    
    
    
@pytest.mark.asyncio
async def test_login_invalid_user():
    login_data = MagicMock(
        email= TEST_EMAIL,
        password = TEST_PASSWORD + "123"
    )
    session = MagicMock()
    
    session_execute_result = MagicMock()
    
    session_execute_result.scalar.return_value = None
    
    session.execute = AsyncMock(return_value=session_execute_result)
    
    result: HTTPException = await AuthManager.login(login_data, session)
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 401
    assert result.detail == "Incorrect email or password"
    
    

    
@pytest.mark.asyncio
async def test_whoami_invalid():
    session = MagicMock()
    
    token = AuthManager.create_access_token({"ema111il": TEST_EMAIL})
    
    result = await AuthManager.whoami(token, session)
    
    assert isinstance(result, UnauthorizedException)
    

@pytest.mark.asyncio
async def test_whoami_valid():
    session = MagicMock()
    
    token = AuthManager.create_access_token({"email": TEST_EMAIL})
    
    
    # select(User).options(joinedload(User.categories)).filter(User.email == email)
    
    exec_result = MagicMock()
    
    exec_result.scalar.return_value = User(email=TEST_EMAIL)
    
    session.execute = AsyncMock(return_value=exec_result)
    
    result = await AuthManager.whoami(token, session)
    
    assert isinstance(result, User)
    
    
    
@pytest.mark.asyncio
async def test_func_get_current_user_valid():
    request = MagicMock()
    request.cookies = {TOKEN_NAME: AuthManager.create_access_token(data={"email": TEST_EMAIL})}
    session = MagicMock()
    
    with patch("managers.AuthManager.AuthManager.whoami", new=AsyncMock(return_value=User(email=TEST_EMAIL))):
        result = await get_current_user(request, session)
        
        assert isinstance(result, User)
        
        assert result.email == TEST_EMAIL
        
        
        
@pytest.mark.asyncio
async def test_func_get_current_user_unauth():
    request = MagicMock()
    request.cookies = {TOKEN_NAME: AuthManager.create_access_token(data={"email": TEST_EMAIL})}
    session = MagicMock()
    
    with patch("managers.AuthManager.AuthManager.whoami", new=AsyncMock(return_value=None)):
        
        
        with pytest.raises(HTTPException) as exc_info:
            result = await get_current_user(request, session)
            
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
            
            
@pytest.mark.asyncio
async def test_func_get_admin_valid():
    user = User(email=TEST_EMAIL, is_admin=True)
    result = await get_admin(user)
    
    assert result==user
    
    
@pytest.mark.asyncio
async def test_func_get_admin_invalid():
    user = User(email=TEST_EMAIL)
    
    with pytest.raises(HTTPException) as exc_info:
        result = await get_admin(user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Forbidden"
    