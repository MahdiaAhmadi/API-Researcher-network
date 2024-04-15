from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from models import User, UpdateUserModel
def responseid_handler(response):
    response["id"] = str(response["_id"])

    return response
def listresponse_handler(responselist):
    for item in responselist:
         item["id"] = str(item["_id"])
    return responselist




# MongoDB connection URL
MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
users_collection = database["users"]
usertype_collection = database["user_type"]

UserRouter = APIRouter()

@UserRouter.get("/users-list")
async def list_users():
    response =  users_collection.find({})
    documents = await response.to_list(length=None)
    documents = listresponse_handler(documents)  # Convert cursor to list
    return documents


@UserRouter.get("/user-type-list")
async def list_usertype():
    response =  usertype_collection.find({})
    documents = await response.to_list(length=None)
    documents = listresponse_handler(documents)   # Convert cursor to list
    return documents

@UserRouter.post("/create-user")
async def create_user(user: User):
    result = await users_collection.insert_one(user.model_dump())
    response = user.model_dump()
    response["id"] = str(result.inserted_id)
    return response

@UserRouter.get("/find-user-by-id/{user_id}")
async def read_item(user_id: str):
    item = await users_collection.find_one({"_id":ObjectId(user_id)})
    if item:
        return item
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="User doens't exists.")

@UserRouter.put("/update-user/{user_id}")
async def update_item(user_id: str, user: User):
    updated_user = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)}, {"$set": user.model_dump()}
    )
    if updated_user:
        return {"id": user_id}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="User doens't exists.")

@UserRouter.delete("/delete-user/{user_id}")
async def delete_user(user_id: str):
    deleted_item = await users_collection.find_one_and_delete({"_id":ObjectId(user_id)})
    if deleted_item:
        return {"response":"User deleted"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="User doens't exists.")
