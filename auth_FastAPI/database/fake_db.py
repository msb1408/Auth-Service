from passlib.context import CryptContext

# Контекст для хэширования

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# словарь для хранения пользователей

fake_users_db = {
    "johndoe": {
        "user_id": 1,
        "name": "John Doe",
        "age": 30,
        "email": "johndoe@example.com",
        "role": "user",
        "hashed_password": pwd_context.hash("password123"),  # здесь будет хэширование
    },
    "admin": {
        "user_id": 2,
        "name": "Admin",
        "age": 35,
        "email": "admin@example.com",
        "role": "admin",
        "hashed_password": pwd_context.hash("password456"),  # здесь будет хэширование
    },
}