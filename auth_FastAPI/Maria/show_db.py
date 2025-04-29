import redis
import json
import os
from passlib.context import CryptContext

# Подключение к Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=0,
    decode_responses=True
)

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def show_all_users():
    print("\n=== Все пользователи ===")
    for key in redis_client.keys("user:*"):
        user_data = redis_client.get(key)
        if user_data:
            user = json.loads(user_data)
            print(f"\nПользователь {key}:")
            for field, value in user.items():
                print(f"  {field}: {value}")

def show_counters():
    print("\n=== Счетчики ===")
    counter = redis_client.get("user_id_counter")
    print(f"Следующий ID пользователя: {counter}")

def add_test_user(name, age, email, role="user", password="Test123!@#"):
    # Получаем следующий ID
    current_id = redis_client.get("user_id_counter")
    if current_id is None:
        user_id = 1
        redis_client.set("user_id_counter", "1")
    else:
        user_id = int(current_id) + 1
        redis_client.set("user_id_counter", str(user_id))

    # Создаем пользователя
    user = {
        "id": user_id,
        "name": name,
        "age": age,
        "email": email,
        "role": role,
        "password_hash": pwd_context.hash(password)
    }

    # Сохраняем в Redis
    redis_client.set(f"user:{user_id}", json.dumps(user))
    print(f"Добавлен пользователь: {name} (ID: {user_id})")

def clear_database():
    print("\nОчистка базы данных...")
    redis_client.flushall()
    print("База данных очищена")

if __name__ == "__main__":
    while True:
        print("\nВыберите действие:")
        print("1. Показать все данные")
        print("2. Добавить тестового пользователя")
        print("3. Очистить базу данных")
        print("4. Выход")
        
        choice = input("Ваш выбор: ")
        
        if choice == "1":
            print("\nДанные в Redis:")
            print("==============")
            print("Все ключи в базе:")
            all_keys = redis_client.keys("*")
            print(", ".join(all_keys))
            show_all_users()
            show_counters()
        
        elif choice == "2":
            name = input("Введите имя: ")
            age = int(input("Введите возраст: "))
            email = input("Введите email: ")
            role = input("Введите роль (user/admin): ")
            add_test_user(name, age, email, role)
        
        elif choice == "3":
            confirm = input("Вы уверены? (y/n): ")
            if confirm.lower() == 'y':
                clear_database()
        
        elif choice == "4":
            break
        
        else:
            print("Неверный выбор") 