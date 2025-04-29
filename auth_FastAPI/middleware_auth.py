#библиотеки
import hashlib
import redis
from fastapi import Request, HTTPException, Depends, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
import httpx

#импорты из файлов
# from services.user_service import get_user
# from routes_8000 import verify_auth
from routers.routes_8001 import LoginRequest

logging.basicConfig(
    format='%(asctime)s - %(message)s', 
    datefmt='%d-%b %H:%M:%S', 
    level=logging.INFO, 
    filename="app.log", 
    filemode="a", 
    encoding='utf8',
    force=True
    )

# test_db = {
#     "admin": {
#         "user_id": 2,
#         "name": "Admin",
#         "age": 35,
#         "email": "admin@example.com",
#         "role": "admin",    
#         "hashed_password": hashlib.sha256("password456".encode()).hexdigest(),  # здесь будет хэширование
#     },
# }


# security = HTTPBasic()
# def validate_creds(credentials: HTTPBasicCredentials = Depends(security)):
#     if credentials.username not in test_db:
#         raise HTTPException(status_code=401, detail="User not found")
    
#     stored_password_hash = test_db.get(credentials.username)['hashed_password']

#     if stored_password_hash is None:
#         raise HTTPException(status_code=401, detail="User not found")
    
#     password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    
#     if isinstance(stored_password_hash, bytes):
#         stored_password_hash = stored_password_hash.decode()

#     if password_hash != stored_password_hash:
#         raise HTTPException(status_code=401, detail="Incorrect password")
    
#     return credentials.username




# еще незакоченная версия

QUERY_URL = "http://127.0.0.1:8003" 
BACKEND_URL = "http://127.0.0.1:8000" 

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # исключения
        path = request.url.path
        if path in ["/docs", "/openapi.json"]:
            return await call_next(request)

        # Логика для /register
        if path == "/register" and request.method == "POST":
            try:
                body = await request.json()
                user = LoginRequest(**body)

                # Асинхронный запрос к Query_Service для проверки существования пользователя
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(f"{QUERY_URL}/check_user", params={"username": user.username}, timeout=5)
                    except httpx.RequestError:
                        return JSONResponse(status_code=503, content={"detail": "Database connection failed"})

                if response.status_code == 200:
                    return JSONResponse(status_code=409, content={"detail": "User already exists"})
                
                elif response.status_code == 404:
                    return JSONResponse(status_code=201, content={"message": "Registered successfully"})
                
                else:
                    raise HTTPException(status_code=response.status_code, detail="Error communicating with database")
                
            except Exception as e:
                return JSONResponse(status_code=400, content={"detail": str(e)})

        # Логика для /signin
        elif path == "/signin" and request.method == "POST":
            try:
                body = await request.json()
                user = LoginRequest(**body)

                # Асинхронный запрос к Query_Service для проверки логина и пароля
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(f"{QUERY_URL}/check_user", params={"username": user.username}, timeout=5)
                    except httpx.RequestError as e:
                        return JSONResponse(status_code=503, content={"detail": "Database connection failed"})
                
                if response.status_code == 200:
                    
                    headers = {
                        "x-username": user.username,
                        "x-user-hashed_password": str(hash(user.password))  
                    }
                    return JSONResponse(
                        status_code=200,
                        content={"message": "Login successfully"},
                        headers=headers  # Заголовки добавляются в HTTP-заголовки ответа
                    )
                elif response.status_code == 401:
                    return JSONResponse(status_code=401, content={"detail": "Invalid username or password"})
                else:
                    raise HTTPException(status_code=response.status_code, detail="Error communicating with database")
            except Exception as e:
                return JSONResponse(status_code=400, content={"detail": str(e)})

        # Логика для остальных маршрутов
        else:
            # Проверяем наличие заголовков x-username и x-user-hashed_password в HTTP-заголовках
            x_username = request.headers.get("x-username")
            x_hashed_password = request.headers.get("x-user-hashed_password")

            if not x_username or not x_hashed_password:
                return JSONResponse(status_code=401, content={"detail": "Invalid user"})

            # Перенаправление запроса на Backend
            async with httpx.AsyncClient() as client:
                try:
                    
                    backend_url = f"{BACKEND_URL}{path}"
                    method = request.method
                    body = None

                    if request.method in ["POST", "GET", "DELETE"]:
                        body = await request.json()

                    # Отправляем запрос на Backend
                    response = await client.request(method, backend_url, json=body, timeout=5.0)

                    # Возвращаем ответ от Backend
                    return JSONResponse(
                        status_code=response.status_code,
                        content=response.json(),
                        headers=dict(response.headers)
                    )
                except httpx.RequestError:
                    return JSONResponse(status_code=503, content={"detail": "Service unavailable"})
                except Exception as e:
                    return JSONResponse(status_code=500, content={"detail": str(e)})