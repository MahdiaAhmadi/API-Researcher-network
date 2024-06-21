from datetime import datetime

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

import users_service
from helpers import (ErrorResponseModel, ResponseModel, addOne, deleteOne,
                     fuzzySearch, get_by_idlist, getAll, getOne, updateOne)
from models import Post, UpdatePost, User

MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
posts_collection = database["posts"]
users_collection = database["users"]
categories_collection = database["categories"]
comments_collection = database["comments"]

PostRouter = APIRouter()

@PostRouter.get("/")
async def list_posts(authorized: bool =  Depends(users_service.verify_token)):
    if(authorized):
        documents = await getAll(posts_collection)
        for post in documents:
            categories = await get_by_idlist(categories_collection, post["categories_id"])
            post["categories"] = categories

        return ResponseModel(documents, "List of all posts")

@PostRouter.get("/user-posts")
async def user_posts(current_user: User = Depends(users_service.get_current_user)):
    posts = await fuzzySearch(posts_collection, "author_id", current_user["id"])
    for post in posts:
        categories = await get_by_idlist(categories_collection, post["categories_id"])
        post["categories"] = categories
    return ResponseModel(posts, "List of user posts")

@PostRouter.post("/")
async def create_post(post: Post, authorized: bool =  Depends(users_service.verify_token)):
    if(authorized):
        post_dict = post.model_dump(by_alias=True)
        response = await addOne(posts_collection, post_dict)
        return ResponseModel(response, "Post was created")

@PostRouter.get("/id/{post_id}")
async def read_item(post_id: str, authorized: bool =  Depends(users_service.verify_token)):
   if(authorized):
        item = await getOne(posts_collection, post_id)
        categories = await get_by_idlist(categories_collection, item["categories_id"])
        comments = await get_by_idlist(comments_collection, item["comments_id"])
        item["categories"] = categories
        item["comments"] = comments
        if item:
            return ResponseModel(item, "Found post")
        return ErrorResponseModel("Error occurred", 400, "post does not exist")


@PostRouter.put("/id/{post_id}")
async def update_item(post_id: str, post: Post, authorized: bool =  Depends(users_service.verify_token)):
    if(authorized):
        updated_post = await updateOne(posts_collection, post_id, post.model_dump())
        if updated_post:
            return ResponseModel({"id": post_id}, "Post sucessfully updated")
        return ErrorResponseModel("Error occurred", 400, "post does not exist")

@PostRouter.put("/like/{post_id}")
async def update_item(post_id: str, current_user: User = Depends(users_service.get_current_user)):
    await users_service.save_liked_post(user_id= current_user["id"], post_id=post_id)
    post:dict = await getOne(posts_collection, post_id)
    post["likes"] += 1
    updated_post = await updateOne(posts_collection, post_id,post)
    if updated_post:
        return ResponseModel({"id": post_id}, "Post sucessfully updated")
    return ErrorResponseModel("Error occurred", 400, "post does not exist")

@PostRouter.delete("/id/{post_id}")
async def delete_post(post_id: str):
    
        deleted_post = await deleteOne(posts_collection, post_id)
        if deleted_post:
            return ResponseModel({"id": post_id}, "Post sucessfully deleted")
        return ErrorResponseModel("Error occurred", 400, "post does not exist")

@PostRouter.get("/by-title")
async def find_by_name(title: str):
    posts = await fuzzySearch(posts_collection, "title", title)
    return ResponseModel(posts, f"All posts that fuzzy match {title}")

@PostRouter.get("/by-author")
async def find_by_name(authorName: str):
    users = await fuzzySearch(users_collection, "display_name", authorName)
    posts =[]
    for user in users:
        find = await fuzzySearch(posts_collection, "author_id", user["id"])
        posts = [*posts,*find]
    return ResponseModel(posts, "All posts")

@PostRouter.get("/by-category")
async def find_by_name(categoryName: str):
    categories = await fuzzySearch(categories_collection, "name", categoryName)
    posts =[]
    for cat in categories:
        find = await fuzzySearch(posts_collection, "categories_id", cat["id"])
        posts = [*posts,*find]
    return ResponseModel(posts, "All posts")



