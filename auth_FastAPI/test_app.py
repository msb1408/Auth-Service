from fastapi.testclient import TestClient
from fastapi import FastAPI
import hashlib

import pytest


from middleware_auth import redis_client
from main import app1


client = TestClient(app1)


@pytest.fixture
def setup_redis():
    """Фикстура для очистки данных в Redis перед тестами"""
    username = "testuser"
    password = "password"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    redis_client.set(username, hashed_password)  # Записываем тестового пользователя
    yield
    redis_client.delete(username)  # Удаляем после теста



def test_get_users_without_auth():
    headers = {
        "X-Allow-Edit": "False",
        }
    response = client.get("/get_users", headers=headers)
    assert response.status_code == 400


def test_get_users_with_auth():
    username = "testuser"
    password = "password" 
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    redis_client.set(username, hashed_password)
    headers = {
        "X-Allow-Edit": "True",
        "X-Username": username,
        "X-User-Hashed-Password": hashed_password
    }
    response = client.get("/get_users", headers=headers)
    assert response.status_code == 200


def test_add_new_user_without_auth():
    headers = {"X-Allow-Edit": "False"}
    response = client.post("/add_new_user", headers=headers) 
    print(response.status_code)
    assert response.status_code == 403
    


def test_add_new_user_with_auth():
    username = "testuser"
    password = "password"  
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  
    redis_client.set(username, hashed_password)
    headers = {
        "X-Allow-Edit": "True",
        "X-Username": username,
        "X-User-Hashed-Password": password  
    }
    response = client.post("/add_new_user", headers=headers)
    assert response.status_code == 200


def test_delete_user_with_wrong_auth():
    headers = {"X-Allow-Edit": "False"}
    response = client.delete("/delete_user", headers=headers)
    assert response.status_code == 403
