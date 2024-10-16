from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class RegisterInput(BaseModel):
    email: EmailStr 
    password: str = Field(min_length = 8, max_length = 256)
    
    
class RegisterSuccessResponse(BaseModel):
    message: str
    user_id: int

class RegisterErrorResponse(BaseModel):
    message: str
    error_code: int
    
    
class LoginInput(BaseModel):
    email: EmailStr 
    password: str = Field(min_length = 8, max_length = 256)
    
    
class LoginSuccessResponse(BaseModel):
    message: str
    user_id: int

class LoginErrorResponse(BaseModel):
    message: str
    error_code: int
    
class UserRead(BaseModel):
    id: int
    email: EmailStr
    creation_date: datetime
    is_admin: bool
    
    
class UnauthorizedError(BaseModel):
    msg: str