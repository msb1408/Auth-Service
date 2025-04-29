from fastapi import HTTPException, Header
from services.user_service import get_user
from models.user import User
from database.fake_db import fake_users_db, pwd_context
from pydantic import EmailStr

def register_user(username: str, password: str):
    user = get_user(username, password)
    if user:
        raise HTTPException(
            status_code=400,
            detail='User already exists'
        )
    new_user = fake_users_db[username] = {
        "user_id": fake_users_db.get(list(fake_users_db.keys())[-1]).get('user_id', None) + 1,
        "name": '',
        "age": '',
        "email": '',
        "role": "",
    }
    new_user["x-username"] = username
    new_user["x-user-hashed-password"] = pwd_context.hash(password)
    return new_user


def authenticate_user(username: str, password: str) -> User:
    user = get_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Custom"},
        )

    user_dict = dict(user) 
    
    user_dict["x-username"] = username
    user_dict["x-user-hashed-password"] = fake_users_db[username]["hashed_password"]
    return user_dict

def check_allow_edit(x_allow_edit: str = Header(...)):
    if x_allow_edit != "True":
        raise HTTPException(status_code=403, detail="Editing not allowed")