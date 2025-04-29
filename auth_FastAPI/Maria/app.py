from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
import redis
from passlib.context import CryptContext

app = FastAPI()

# Подключение к Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API-ключ для защиты эндпоинтов (можно заменить на JWT)
API_KEY = "secret_key"

# Pydantic-схема для валидации данных пользователя
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=5, description="Password must be at least 5 characters")


# Функция для проверки API-ключа
def check_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/users")
def get_users():
    
    users = r.keys("user:*")  # Получаем всех пользователей
    return {"users": users}


@app.post("/add_user")
def add_user(user: UserCreate, api_key: str = Depends(check_api_key)):
    
    if r.exists(f"user:{user.username}"):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(user.password)  # Хэшируем пароль
    r.hset(f"user:{user.username}", mapping={"username": user.username, "password": hashed_password})
    return {"message": "User added successfully"}


@app.delete("/delete_user")
def delete_user(username: str, api_key: str = Depends(check_api_key)):
   
    if not r.exists(f"user:{username}"):
        raise HTTPException(status_code=404, detail="User not found")

    r.delete(f"user:{username}")  # Удаляем пользователя
    return {"message": "User deleted successfully"}


@app.post("/login")
def login(username: str, password: str):
    user = r.hgetall(f"user:{username}")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not pwd_context.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Login successful"}


@app.post("/logout")
def logout(username: str, api_key: str = Depends(check_api_key)):
    r.delete(f"user:{username}")
    return {"message": "Logout successful"}

