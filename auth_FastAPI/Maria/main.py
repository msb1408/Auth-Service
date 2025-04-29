from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/", summary = 'Главная ручка', tags=['Основные ручки'])
def home():
    return "hi"

if __name__ == '__main__':
    uvicorn.run("main.app")
#fastapi dev main.py
#uvicorn main:app --reload