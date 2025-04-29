import redis

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Записываем пользователя
user_id = 1
r.hset(f"user_id:{user_id}", mapping={
    "name": "Alice",
    "age": "25",
    "email": "alice@example.com",
    "role": "admin",
    "id": str(user_id)
})

# Получаем и выводим
user = r.hgetall(f"user_id:{user_id}")
print("User from Redis:", user)  # <-- Добавлен print
