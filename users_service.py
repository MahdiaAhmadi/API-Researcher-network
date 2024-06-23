from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import Annotated

from auth import (CREDENTIALS_EXCEPTION, Token, create_access_token,
                  decode_access_token, oauth2_scheme)
from helpers import (ErrorResponseModel, ResponseModel, addOne, deleteOne,
                     getAll, getFromIDList, getOne, responseid_handler,
                     updateOne)
from models import AccountCreate, Ban, LoginUser, UpdateUserModel, User, UserType

MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
users_collection = database["users"]
usertype_collection = database["user_type"]

async def get_current_user(req: Request):
    token = req.headers["Authorization"]
    print(token)
    user_id = decode_access_token(token)
    if user_id is None:
        raise CREDENTIALS_EXCEPTION
    item = await getOne(users_collection, user_id)
    if item is None:
        raise CREDENTIALS_EXCEPTION
    return item

def is_admin(current_user: User):
    print(current_user)
    if "user_type" not in current_user.keys():
        return False
    creds = current_user["user_type"]
    return creds["code"] == 1 and creds["type"] == "admin"

def verify_token(req: Request):
    token = req.headers["Authorization"]
    user_id = decode_access_token(token)
    if user_id is None:
        raise CREDENTIALS_EXCEPTION
    return True

UserRouter = APIRouter()

@UserRouter.post("/token")
async def get_secure_login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await login(credentials.username, credentials.password)
    print(credentials)
    if(user is None):
        return ErrorResponseModel("Unauthenticated", 401, "User not authenticated")
    access_token = create_access_token(user["id"])
    return Token(access_token=access_token)



@UserRouter.post("/login")
async def get_login(credentials:LoginUser):
    user = await login(credentials.username, credentials.password)    
    print(credentials)
    if(user is None):
        return ErrorResponseModel("Unauthenticated", 401, "User not authenticated")
    return ResponseModel(user, "Logged User")


@UserRouter.get("/by-token")
async def get_login(current_user: User =  Depends(get_current_user)):
    return ResponseModel(current_user, "Current Logged User")

@UserRouter.put("/change-password")
async def get_login(newPassword:str,current_user: User =  Depends(get_current_user)):
    user = current_user
    user["password"]= newPassword
    updated_user = await updateOne(users_collection, current_user["id"], user)
    if updated_user:
        return ResponseModel({"id": current_user["id"]}, "Paswword Changed")
    return ErrorResponseModel("Error occurred", 404, "user does not exist")

@UserRouter.get("/users-list")
async def list_users():
    documents = await getAll(users_collection)
    return ResponseModel(documents, "List of all users")

@UserRouter.get("/banned-users")
async def banned_users(current_user: User = Depends(get_current_user)):
    if(is_admin(current_user)):
        users = await getAll(users_collection)
        banned = list(filter(lambda p: "banned_status" in p.keys() and (p["banned_status"]["permanent"] or p["banned_status"]["endDate"] > datetime.now()), users))
        return ResponseModel(banned, "List of all banned users")
    raise CREDENTIALS_EXCEPTION


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
    userModel = User(**user)
    print(userModel)
    response = await addOne(users_collection, userModel.model_dump())
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
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    if(is_admin(current_user)):
        item = await getOne(users_collection, user_id)
        ban = Ban(permanent=True,endDate=datetime.now())
        deleted_user = await updateOne(users_collection, user_id, {"banned_status": ban.model_dump()})
        if deleted_user:
            return ResponseModel({"id": user_id}, "User sucessfully deleted")
    return ErrorResponseModel("Error occurred", 404, "user does not exist")

@UserRouter.delete("/suspend-user/{user_id}")
async def suspend_user(user_id: str, suspension_days: int, current_user: User = Depends(get_current_user)):
    if(is_admin(current_user)):
        item = await getOne(users_collection, user_id)
        ban = Ban(permanent=False, endDate=datetime.now() + timedelta(days=suspension_days))
        suspended_user = await updateOne(users_collection, user_id, {"banned_status": ban.model_dump()})
        if suspended_user:
            return ResponseModel({"id": user_id}, f'User was suspended for {suspension_days} days')
    return ErrorResponseModel("Error occurred", 404, "user does not exist")

@UserRouter.post("/follow-user/{author_id}")
async def create_user(author_id: str, current_user: User =  Depends(get_current_user)):
    user:dict = current_user
    follwed_user:dict = await getOne(users_collection, author_id)

    try:
        if author_id not in user["follows_id"]:
            user["follows_id"].append(author_id)
    except:
         user["follows_id"] = [author_id]
    try:
        if current_user["id"] not in follwed_user["followers_id"]:
            follwed_user["followers_id"].append(current_user["id"])
    except:
         follwed_user["followers_id"] = [current_user["id"]]
    
    updated_follwed = await updateOne(users_collection, author_id, follwed_user)
    updated_user = await updateOne(users_collection, current_user["id"], user)
    if updated_user and updated_follwed:
        return ResponseModel({"id": current_user["id"]}, "User followed")
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



@UserRouter.get("/me")
async def read_users_me( current_user: Annotated[User, Depends(get_current_user)]):
    print(current_user)
    return ResponseModel(current_user, "Current Logged User")

@UserRouter.get("/me/posts")
async def get_all_posts_from_me(current_user: Annotated[User, Depends(get_current_user)]):
    user_id = current_user["id"]
    posts = await getFromIDList(users_collection, "_id", user_id, "posts_id", database["posts"])
    return ResponseModel(posts, f"All posts from user {user_id}")

@UserRouter.put("/me/update")
async def update_me(user: UpdateUserModel, current_user: Annotated[User, Depends(get_current_user)]):
    # user_id = decode_access_token(token)
    user_id = current_user["id"]
    print("updating")
    updated_user = await updateOne(users_collection, user_id, user.model_dump(exclude_unset=True))
    if updated_user:
        return ResponseModel({"id": user_id}, "User sucessfully updated")
    return ErrorResponseModel("Error occurred", 404, "user does not exist")
