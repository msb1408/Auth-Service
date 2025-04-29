from pydantic import BaseModel

class User(BaseModel):
    user_id: int
    name: str
    age: int
    email: str
    role: str