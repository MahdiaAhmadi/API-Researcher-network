from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter

from models import Category
from helpers import ErrorResponseModel, ResponseModel, addOne, deleteOne, getAll, getOne, updateOne

MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
categories_collection = database["categories"]

CategoryRouter = APIRouter()

@CategoryRouter.get("/")
async def list_categories():
    documents = await getAll(categories_collection)
    return ResponseModel(documents, "List of all categories")

@CategoryRouter.category("/")
async def create_category(category: Category):
    response = await addOne(categories_collection, category.model_dump())
    return ResponseModel(response, "Category was created")

@CategoryRouter.get("/{category_id}")
async def read_category(category_id: str):
    item = await getOne(categories_collection, category_id)
    if item:
        return ResponseModel(item, "Found category")
    return ErrorResponseModel("Error occurred", 404, "category does not exist")

@CategoryRouter.put("/{category_id}")
async def update_category(category_id: str, category: Category):
    updated_category = await updateOne(categories_collection, category_id, category.model_dump())
    if updated_category:
        return ResponseModel({"id": category_id}, "Category sucessfully updated")
    return ErrorResponseModel("Error occurred", 404, "category does not exist")

@CategoryRouter.delete("/{category_id}")
async def delete_category(category_id: str):
    deleted_category = await deleteOne(categories_collection, category_id)
    if deleted_category:
        return ResponseModel({"id": category_id}, "Category sucessfully deleted")
    return ErrorResponseModel("Error occurred", 404, "category does not exist")
