from bson.objectid import ObjectId
from fastapi import APIRouter, Body, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, decode_access_token, oauth2_scheme, Token
from typing import Annotated

from helpers import (ErrorResponseModel, ResponseModel, addOne, deleteOne,
                     getAll, getFromIDList, getOne, responseid_handler,
                     updateOne)
from models import AccountCreate, LoginUser, User, UserType

# MongoDB connection URL
MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
users_collection = database["users"]
usertype_collection = database["user_type"]

UserRouter = APIRouter()

@UserRouter.post("/token")
async def get_secure_login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await login(credentials.username, credentials.password)
    print(credentials)
    if(user is None):
        return ErrorResponseModel("Unauthenticated", 401, "User not authenticated")
    print(user)
    access_token = create_access_token(user["id"])
    return Token(username=user["username"], email=user["email"], display_name=user["display_name"], access_token=access_token, token_type="bearer")



@UserRouter.post("/login")
async def get_login(credentials:LoginUser):
    user = await login(credentials.username, credentials.password)    
    print(credentials)
    if(user is None):
        return ErrorResponseModel("Unauthenticated", 401, "User not authenticated")
    return ResponseModel(user, "Logged User")

@UserRouter.get("/users-list")
async def list_users():
    documents = await getAll(users_collection)
    return ResponseModel(documents, "List of all users")


@UserRouter.get("/user-type-list")
async def list_usertype():
    documents = await getAll(usertype_collection)
    return ResponseModel(documents, "List of all available user types")

@UserRouter.post("/create-user")
async def create_user(create_user: AccountCreate):
    user:dict = create_user.model_dump()
    print(user)
    default_type = await get_default_user_type()
    print(default_type)
    user["user_type"] = default_type
    response = await addOne(users_collection, user)
    return ResponseModel(response, "User was created")

@UserRouter.get("/id/{user_id}")
async def read_item(user_id: str):
    item = await getOne(users_collection, user_id)
    if item:
        return ResponseModel(item, "Found user")
    return ErrorResponseModel("Error occurred", 404, "user does not exist")

@UserRouter.get("/id/{user_id}/posts")
async def get_all_posts_from_user(user_id: str):
    posts = await getFromIDList(users_collection, "_id", user_id, "posts_id", database["posts"])
    return ResponseModel(posts, f"All posts from user {user_id}")

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


async def login(username, password):
    user = await users_collection.find_one({"username": username, "password":password})
    if user:
        return responseid_handler(user)
    return None

async def get_default_user_type():
    user_type = await usertype_collection.find_one({"code":3})
    return responseid_handler(user_type) 

async def save_liked_post(user_id:str, post_id:str):
    user:dict = await getOne(users_collection, user_id)
    print(user)
    try:
        if post_id not in user["liked_posts_id"]:
            user["liked_posts_id"].append(post_id)
        else:
            user["liked_posts_id"].remove(post_id)
    except:
        user["liked_posts_id"] = [post_id]
    finally:
        await updateOne(users_collection, user_id, user)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(token)
    user_id = decode_access_token(token)
    print(user_id)
    if user_id is None:
        raise credentials_exception
    item = await getOne(users_collection, user_id)
    if item is None:
        raise credentials_exception
    return item

@UserRouter.get("/me")
async def read_users_me( current_user: Annotated[User, Depends(get_current_user)]):
    print(current_user)
    return current_user

@UserRouter.get("/me/posts")
async def get_all_posts_from_me(token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = decode_access_token(token)
    posts = await getFromIDList(users_collection, "_id", user_id, "posts_id", database["posts"])
    return ResponseModel(posts, f"All posts from user {user_id}")
