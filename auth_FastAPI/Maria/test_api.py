import requests

# Базовый URL
BASE_URL = "http://localhost:8000"

# Добавление пользователя
def add_user():
    headers = {
        "Content-Type": "application/json",
        "x-allow-edit": "ok"
    }
    data = {
        "name": "Иван Петров",
        "age": 25,
        "email": "ivan@example.com",
        "role": "user"
    }
    response = requests.post(f"{BASE_URL}/add_user", json=data, headers=headers)
    print("Ответ:", response.json())

# Получение списка пользователей
def get_users():
    response = requests.get(f"{BASE_URL}/users")
    print("Список пользователей:", response.json())

if __name__ == "__main__":
    print("Добавляем пользователя...")
    add_user()
    print("\nПолучаем список пользователей...")
    get_users() 