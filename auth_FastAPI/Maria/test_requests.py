import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response):
    print(f"Статус: {response.status_code}")
    print("Ответ:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    print("-" * 50)

# 1. Получение списка пользователей
def get_users():
    print("\n1. Получение списка пользователей:")
    response = requests.get(f"{BASE_URL}/users")
    print_response(response)

# 2. Добавление нового пользователя
def add_user():
    print("\n2. Добавление нового пользователя:")
    new_user = {
        "name": "Мария Сидорова",
        "age": 28,
        "email": "maria@example.com",
        "role": "user"
    }
    headers = {
        "Content-Type": "application/json",
        "x-allow-edit": "true"
    }
    response = requests.post(f"{BASE_URL}/add_user", json=new_user, headers=headers)
    print_response(response)

# 3. Попытка добавить пользователя с существующим email
def add_duplicate_user():
    print("\n3. Попытка добавить пользователя с существующим email:")
    new_user = {
        "name": "Другая Мария",
        "age": 30,
        "email": "maria@example.com",  # тот же email
        "role": "user"
    }
    headers = {
        "Content-Type": "application/json",
        "x-allow-edit": "true"
    }
    response = requests.post(f"{BASE_URL}/add_user", json=new_user, headers=headers)
    print_response(response)

# 4. Вход в систему
def sign_in():
    print("\n4. Вход в систему:")
    response = requests.post(
        f"{BASE_URL}/sign-in",
        params={"email": "maria@example.com", "password": "test123"}
    )
    print_response(response)

# 5. Удаление пользователя
def delete_user(user_id):
    print(f"\n5. Удаление пользователя с ID {user_id}:")
    headers = {"x-allow-edit": "true"}
    response = requests.delete(f"{BASE_URL}/delete_user/{user_id}", headers=headers)
    print_response(response)

if __name__ == "__main__":
    # Выполняем все тесты
    get_users()
    add_user()
    add_duplicate_user()  # Должен вернуть ошибку 409
    sign_in()
    delete_user(1)  # Удаляем пользователя с ID 1
    get_users()  # Проверяем список после удаления 