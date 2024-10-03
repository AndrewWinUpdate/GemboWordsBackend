from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from routers.test_router import router as test_router

app = FastAPI()

origins = [
    "*",                        # Разрешить доступ с любых доменов (не рекомендуется в продакшене)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Список разрешенных доменов
    allow_credentials=True,   # Разрешить отправку куки и авторизацию
    allow_methods=["*"],      # Разрешить любые HTTP-методы (GET, POST и т.д.)
    allow_headers=["*"],      # Разрешить любые заголовки
)

app.include_router(test_router)



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}