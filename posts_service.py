from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import Annotated

import users_service
from auth import CREDENTIALS_EXCEPTION
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

        visible_posts = list(filter(lambda p: p["visibility"] > 0, documents))
        print(visible_posts)
        return ResponseModel(visible_posts, "List of all posts")

@PostRouter.get("/user-posts")
async def user_posts(current_user: User = Depends(users_service.get_current_user)):
    posts = await fuzzySearch(posts_collection, "author_id", current_user["id"])
    for post in posts:
        categories = await get_by_idlist(categories_collection, post["categories_id"])
        post["categories"] = categories

    visible_posts = list(filter(lambda p: p["visibility"] > 0, posts))
    return ResponseModel(visible_posts, "List of user posts")

@PostRouter.get("/reported-posts")
async def reported_posts(current_user: User = Depends(users_service.get_current_user)):
    if(users_service.is_admin(current_user)):
        posts = await getAll(posts_collection)
        reported = list(filter(lambda p: "reports" in p.keys() and len(p["reports"]) > 0, posts))
        for post in reported:
            categories = await get_by_idlist(categories_collection, post["categories_id"])
            post["categories"] = categories
        return ResponseModel(reported, "List of all reported posts")
    raise CREDENTIALS_EXCEPTION

@PostRouter.get("/banned-posts")
async def banned_posts(current_user: User = Depends(users_service.get_current_user)):
    if(users_service.is_admin(current_user)):
        posts = await getAll(posts_collection)
        banned = list(filter(lambda p: p["visibility"] == 0, posts))
        for post in banned:
            categories = await get_by_idlist(categories_collection, post["categories_id"])
            post["categories"] = categories
        return ResponseModel(banned, "List of all banned posts")
    raise CREDENTIALS_EXCEPTION

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
async def update_item(post_id: str, post: UpdatePost, authorized: bool =  Depends(users_service.verify_token)):
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
async def delete_post(post_id: str, current_user: User = Depends(users_service.get_current_user)):
        post:dict = await getOne(posts_collection, post_id)
        if post["author_id"] == current_user["id"] or users_service.is_admin(current_user):
            deleted_post = await updateOne(posts_collection, post_id, { "visibility":0})
        else:
            raise CREDENTIALS_EXCEPTION
        if deleted_post:
            return ResponseModel({"id": post_id}, "Post sucessfully deleted")
        return ErrorResponseModel("Error occurred", 400, "post does not exist")

@PostRouter.get("/by-title")
async def find_by_name(title: str,authorized: bool =  Depends(users_service.verify_token)):
    if(authorized):
        posts = await fuzzySearch(posts_collection, "title", title)
        for post in posts:
            categories = await get_by_idlist(categories_collection, post["categories_id"])
            post["categories"] = categories
        return ResponseModel(posts, f"All posts that fuzzy match {title}")

@PostRouter.get("/by-author")
async def find_by_name(authorName: str,authorized: bool =  Depends(users_service.verify_token)):
    if(authorized):
        users = await fuzzySearch(users_collection, "display_name", authorName)
        posts =[]
        for user in users:
            find = await fuzzySearch(posts_collection, "author_id", user["id"])
            posts = [*posts,*find]

        for post in posts:
            categories = await get_by_idlist(categories_collection, post["categories_id"])
            post["categories"] = categories
        return ResponseModel(posts, "All posts")

@PostRouter.get("/by-category")
async def find_by_name(categoryName: str,authorized: bool =  Depends(users_service.verify_token)):
    if(authorized):
        categories = await fuzzySearch(categories_collection, "name", categoryName)
        posts =[]
        for cat in categories:
            find = await fuzzySearch(posts_collection, "categories_id", cat["id"])
            posts = [*posts,*find]
        
        for post in posts:
            categories = await get_by_idlist(categories_collection, post["categories_id"])
            post["categories"] = categories
        return ResponseModel(posts, "All posts")

@PostRouter.post("/report-post")
async def report_post(postId: Annotated[str, Body(embed=True)], reason: Annotated[str, Body(embed=True)], current_user: User = Depends(users_service.get_current_user)):
    print("reporting")
    report = {"user_id": current_user["id"], "reason":reason}
    post:dict = await getOne(posts_collection, postId)
    current_reports = post["reports"] if "reports" in post.keys() else []
    for r in current_reports:
        if report["user_id"] == r["user_id"]:
            return ResponseModel(False, "Post already reported")
    current_reports.append(report)
    updated = await updateOne(posts_collection, postId, { "reports": current_reports })
    return ResponseModel(updated, "Post was reported")
