from typing import Union

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware


from routers.test_router import router as test_router
from routers.admin import router as admin_router
from routers.user import router as user_router
import models
from database import engine


from sqladmin import Admin, ModelView

app = FastAPI()


api_router = APIRouter(
    prefix="/api"
)


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

api_router.include_router(test_router)
api_router.include_router(admin_router)
api_router.include_router(user_router)




app.include_router(api_router)



test_mode = 1
if test_mode:
    class UserAdmin(ModelView, model=models.User):
        column_list = [models.User.id, models.User.email]
        
    class CategoryAdmin(ModelView, model=models.Category):
        column_list = [models.Category.id, models.Category.name, models.Category.owner_id, models.Category.words]
        
    class WordAdmin(ModelView, model=models.Word):
        column_list = [models.Word.id, models.Word.english, models.Word.russian, models.Word.owner_id, models.Word.examples]
        
    class ExampleAdmin(ModelView, model=models.Example):
        column_list = [models.Example.id, models.Example.english, models.Example.russian, models.Example.word_id, models.Example.owner_id]

    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(WordAdmin)
    admin.add_view(ExampleAdmin)




@app.get("/")
def read_root():
    return {"Hello": "World!!!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}