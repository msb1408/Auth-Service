from passlib.context import CryptContext
from database.fake_db import fake_users_db
from models.user import User

# Контекст для хэширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширование пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Проверка совпадения пароля с хэшем
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Вернуть пользователя, если верный пароль
def get_user(username: str, password: str) -> User | None:
    user_data = fake_users_db.get(username)
    if user_data and verify_password(password, user_data["hashed_password"]):
        return User(**user_data)
    return None