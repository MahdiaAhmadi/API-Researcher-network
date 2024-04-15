from helpers import ErrorResponseModel, ResponseModel, addOne, deleteOne, getAll, getOne, updateOne
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from models import User, UpdateUserModel

# MongoDB connection URL
MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
users_collection = database["users"]
usertype_collection = database["user_type"]

UserRouter = APIRouter()

@UserRouter.get("/users-list")
async def list_users():
    documents = await getAll(users_collection)
    return ResponseModel(documents, "List of all users")


@UserRouter.get("/user-type-list")
async def list_usertype():
    documents = await getAll(usertype_collection)
    return ResponseModel(documents, "List of all available user types")

@UserRouter.post("/create-user")
async def create_user(user: User):
    response = await addOne(users_collection, user.model_dump())
    return ResponseModel(response, "User was created")

@UserRouter.get("/find-user-by-id/{user_id}")
async def read_item(user_id: str):
    item = await getOne(users_collection, user_id)
    if item:
        return ResponseModel(item, "Found user")
    return ErrorResponseModel("Error occurred", 404, "user does not exist")

@UserRouter.put("/update-user/{user_id}")
async def update_item(user_id: str, user: User):
    updated_user = await updateOne(users_collection, user_id, user.model_dump())
    if updated_user:
        return ResponseModel({"id": user_id}, "User sucessfully updated")
    return ErrorResponseModel("Error occurred", 404, "user does not exist")

@UserRouter.delete("/delete-user/{user_id}")
async def delete_user(user_id: str):
    deleted_user = await deleteOne(users_collection, user_id)
    if deleted_user:
        return ResponseModel({"id": user_id}, "User sucessfully deleted")
    return ErrorResponseModel("Error occurred", 404, "user does not exist")
