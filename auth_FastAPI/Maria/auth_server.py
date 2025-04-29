from fastapi import FastAPI, Header, Depends, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
from passlib.context import CryptContext
from models import UserCreate, UserResponse
import uvicorn
from typing import List
import json
import os

app = FastAPI()

# Подключаем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Подключение к Redis с использованием переменных окружения
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=0,
    decode_responses=True
)

# Инициализация тестовых данных при запуске
def init_test_data():
    # Проверяем, есть ли уже данные
    if not redis_client.keys("user:*"):
        test_users = [
            {
                "id": 1,
                "name": "Тестовый Пользователь",
                "age": 30,
                "email": "test@example.com",
                "role": "admin"
            },
            {
                "id": 2,
                "name": "Анна Иванова",
                "age": 25,
                "email": "anna@example.com",
                "role": "user"
            }
        ]
        
        # Добавляем тестовых пользователей в Redis
        for user in test_users:
            redis_client.set(f"user:{user['id']}", json.dumps(user))
        
        # Устанавливаем счетчик ID
        redis_client.set("user_id_counter", "2")

# Вызываем инициализацию при запуске
init_test_data()

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Пропускаем маршрут sign-in и register без проверки
        if request.url.path in ["/sign-in", "/register", "/"]:
            return await call_next(request)

        # Проверяем защищенные маршруты
        protected_routes = ["/add_user", "/delete_user"]
        if request.url.path in protected_routes:
            x_allow_edit = request.headers.get("x-allow-edit")
            if not x_allow_edit or x_allow_edit != "ok":
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Missing x-allow-edit header"}
                )

        return await call_next(request)

app.add_middleware(AuthMiddleware)

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_next_id() -> int:
        current_id = redis_client.get("user_id_counter")
        if current_id is None:
            redis_client.set("user_id_counter", "1")
            return 1
        new_id = int(current_id) + 1
        redis_client.set("user_id_counter", str(new_id))
        return new_id

def get_header(x_allow_edit: str = Header(None)):
    if x_allow_edit != "ok":
        raise HTTPException(status_code=403, detail="Missing x-allow-edit header")
    return x_allow_edit

@app.get("/users", response_model=List[UserResponse])
async def get_users():
    """Получение списка всех пользователей"""
    users = []
    for key in redis_client.keys("user:*"):
        user_data = redis_client.get(key)
        if user_data:
            user = json.loads(user_data)
            users.append(UserResponse(**user))
    return users

@app.post("/add_user", response_model=UserResponse)
async def add_user(user: UserCreate,  x_allow_edit: str = Depends(get_header)):
    """Добавление нового пользователя"""
    user_id = UserService.get_next_id()
    
    # Создаем полного пользователя с ID и хешированным паролем
    full_user = {
        "id": user_id,
        "name": user.name,
        "age": user.age,
        "email": user.email,
        "role": user.role,
        "password_hash": UserService.hash_password(user.password)
    }
    
    # Проверяем существование пользователя с таким email
    for key in redis_client.keys("user:*"):
        existing_user_data = redis_client.get(key)
        if existing_user_data:
            existing_user = json.loads(existing_user_data)
            if existing_user["email"] == user.email:
                raise HTTPException(status_code=409, detail="User with this email already exists")
    
    # Сохраняем пользователя в Redis
    redis_client.set(f"user:{user_id}", json.dumps(full_user))
    return UserResponse(**{k: v for k, v in full_user.items() if k != "password_hash"})

@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: int, x_allow_edit: str = Depends(get_header)):
    """Удаление пользователя по ID"""
    key = f"user:{user_id}"
    if not redis_client.exists(key):
        raise HTTPException(status_code=404, detail="User not found")
    
    redis_client.delete(key)
    return {"message": "User deleted successfully"}

@app.post("/sign-in")
async def sign_in(email: str, password: str):
    """Маршрут для авторизации"""
    # Ищем пользователя по email
    for key in redis_client.keys("user:*"):
        user_data = redis_client.get(key)
        if user_data:
            user = json.loads(user_data)
            if user["email"] == email:
                # Проверяем пароль
                if UserService.verify_password(password, user["password_hash"]):
                    return {"message": "Successfully signed in", "user": {k: v for k, v in user.items() if k != "password_hash"}}
                else:
                    raise HTTPException(status_code=401, detail="Invalid password")
    
    raise HTTPException(status_code=401, detail="User not found")

@app.get("/register")
async def register_page(request: Request):
    """Страница регистрации пользователя"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/")
async def root():
    """Редирект на страницу регистрации"""
    return RedirectResponse(url="/register")

if __name__ == "__main__":
    uvicorn.run(app)
