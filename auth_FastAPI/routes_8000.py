# импорты библиотек
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import hashlib
import logging

# импорты из файлов
import config as c
# from middleware_auth import redis_client
# from middleware_auth import validate_creds
router = APIRouter()

logging.basicConfig(
    format='%(asctime)s - %(message)s', 
    datefmt='%d-%b %H:%M:%S', 
    level=logging.INFO, 
    filename="app.log", 
    filemode="a", 
    encoding='utf8',
    force=True
    )

# Конфигурация
POSTGRES_SERVICE_URL = "http://localhost:8003"  # URL Postgres-сервиса

security = c.AuthX(config=c.config)

# class UserLoginSchema(BaseModel):
#     username: str
#     password: str


# Модели данных
class UserCreate(BaseModel):
    user_id: int
    name: str
    age: int
    email: str
    role: str
    username: str
    hashed_password: str

# Проверка наличия x-username и x-user-hashed-password
def verify_auth(request: Request):
    # Получает значения заголовков из HTTP-запроса
    x_username = request.headers.get("x-username")
    x_password = request.headers.get("x-user-hashed-password")
    if not (x_username and x_password):
        raise HTTPException(status_code=401, detail="Missing authentication headers")
    return {"username": x_username, "hashed_password": x_password}

# Маршруты
@router.post("/add_user")
async def add_user(user_data: UserCreate, request: Request):
    # Получить словарь или ошибку
    auth = verify_auth(request)
    
    # Переадресация запроса к Postgres (8003)
    async with httpx.AsyncClient() as client:
        postgres_response = await client.post(
            f"{POSTGRES_SERVICE_URL}/add_user", # Куда отправлять запрос
            json=user_data.dict(),# конвертирует Pydantic-модель в словарь (тело запроса)
            headers={"X-Username": auth["username"], "X-User-Hashed-Password": auth["hashed_password"]} # заголовки
        )
    
    # Отправить результат обратно на auth-сервис (8001)
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.post(
                "http://localhost:8001/handle_result",  # Новый эндпоинт на auth-сервисе
                json=postgres_response.json(),
                headers={"Content-Type": "application/json"}
            )
        except httpx.ConnectError:
            # Если auth-сервис недоступен
            return JSONResponse( content={"error": "Auth service unavailable"}, status_code=503)
    
    # Вернуть ответ клиенту
    return JSONResponse(content=auth_response.json(), status_code=auth_response.status_code)

@router.delete("/delete_user/{user_id}")
async def delete_user(user_id: int, request: Request):

    auth = verify_auth(request)
    
    async with httpx.AsyncClient() as client:
        postgres_response = await client.delete(
            f"{POSTGRES_SERVICE_URL}/delete_user/{user_id}",
            headers={"X-Username": auth["username"], "X-User-Hashed-Password": auth["hashed_password"]}
        )
    
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.delete(
                "http://localhost:8001/handle_result",
                json=postgres_response.json(),
                headers={"Content-Type": "application/json"}
            )
        except httpx.ConnectError:
            return JSONResponse( content={"error": "Auth service unavailable"}, status_code=503)

    return JSONResponse( content=auth_response.json(), status_code=auth_response.status_code)

@router.get("/get_all_users")
async def get_all_users(request: Request):

    auth = verify_auth(request)
    
    async with httpx.AsyncClient() as client:
        postgres_response = await client.get(
            f"{POSTGRES_SERVICE_URL}/get_all_users",
            headers={"X-Username": auth["username"], "X-User-Hashed-Password": auth["hashed_password"]}
        )
    
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "http://localhost:8001/handle_result",
                json=postgres_response.json(),
                headers={"Content-Type": "application/json"}
            )
        except httpx.ConnectError:
            return JSONResponse( content={"error": "Auth service unavailable"}, status_code=503)

    return JSONResponse( content=auth_response.json(), status_code=auth_response.status_code)