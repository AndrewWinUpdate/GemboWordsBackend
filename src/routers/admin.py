from fastapi import APIRouter, File, UploadFile
import schemas.User as user_schemas
from typing import Union, List
import schemas.admin_wac as admin_wac


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/global_categories", response_model=List[admin_wac.CategoryReadWithWords])
async def global_categories_read():
    ...



@router.get("/category", response_model=admin_wac.CategoryReadWithWords)
async def category_read(id: int):
    ...

@router.post("/category", response_model=admin_wac.CategoryReadWithoutWords)
async def category_create(name: str, filename: str):
    ...

@router.put("/category", response_model=admin_wac.CategoryReadWithoutWords)
async def category_update(data: admin_wac.CategoryUpdate):
    ...
    
@router.delete("/category")
async def category_delete(id: int):
    ...
    
    
    
@router.get("/word", response_model=admin_wac.WordReadWithoutCategories)
async def word_read(id: int):
    ...

@router.post("/word", response_model=admin_wac.WordReadWithCategories)
async def word_create(name: str, filename: str):
    ...

@router.put("/word", response_model=admin_wac.WordReadWithCategories)
async def word_update(data: admin_wac.WordUpdate):
    ...
    
@router.delete("/word")
async def word_delete(id: int):
    ...