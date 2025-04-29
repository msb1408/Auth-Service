from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from typing import Optional

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=150)
    email: EmailStr
    role: str
    password_hash: str

    @field_validator('name')
    def validate_name(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('Имя должно содержать только буквы и пробелы')
        return v.strip()

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=0, le=150)
    email: EmailStr
    role: str
    password: str = Field(..., min_length=8, max_length=50)

    @field_validator('name')
    def validate_name(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('Имя должно содержать только буквы и пробелы')
        return v.strip()

    @field_validator('password')
    def validate_password(cls, v):
        # Минимум 8 символов
        if len(v) < 8:
            raise ValueError('Пароль должен быть не менее 8 символов')
        
        # Должен содержать хотя бы одну цифру
        if not any(char.isdigit() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        
        # Должен содержать хотя бы одну букву в верхнем регистре
        if not any(char.isupper() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        
        # Должен содержать хотя бы одну букву в нижнем регистре
        if not any(char.islower() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        
        # Должен содержать хотя бы один специальный символ
        special_chars = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if not special_chars.search(v):
            raise ValueError('Пароль должен содержать хотя бы один специальный символ (@_!#$%^&*()<>?/\|}{~:)')
        
        return v

    @field_validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'admin']
        if v.lower() not in allowed_roles:
            raise ValueError(f'Роль должна быть одной из: {", ".join(allowed_roles)}')
        return v.lower()

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr
    role: str 