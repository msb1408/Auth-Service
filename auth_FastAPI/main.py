# импорт библиотек
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# импорты из файлов
from routes_8000 import router as router_8000
from routers.routes_8001 import router as router_8001
from middleware_auth import AuthMiddleware

app_8000 = FastAPI()
app_8001 = FastAPI()
# app_8003 = FastAPI()


# origins = [
#        "http://localhost:8001/",
#        "http://localhost:8000/",
#        "http://127.0.0.1:8000/",
#        "http://127.0.0.1:8001/",
#        ]
app_8000.include_router(router_8000)
app_8001.include_router(router_8001)

app_8001.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"], 
                   allow_headers=["*"],  
                   )
app_8000.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"], 
                   allow_headers=["*"],  
                   )
# app_8003.add_middleware(CORSMiddleware,
#                    allow_origins=["*"],
#                    allow_credentials=True,
#                    allow_methods=["*"], 
#                    allow_headers=["*"],  
#                    )
# app_8000.add_middleware(AuthMiddleware)
app_8001.add_middleware(AuthMiddleware)


    

async def run_server(app, port):
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        run_server(app_8000, 8000),
        run_server(app_8001, 8001),
        # run_server(app_8003, 8001),
    )
# запуск

if __name__ == '__main__':
#     uvicorn.run('main:app', reload=True, host='localhost', port=8001)
       asyncio.run(main())