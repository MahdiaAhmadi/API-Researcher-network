from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter

from models import Post
from helpers import ErrorResponseModel, ResponseModel, addOne, deleteOne, getAll, getOne, updateOne

MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
posts_collection = database["posts"]

PostRouter = APIRouter()

@PostRouter.get("/")
async def list_posts():
    documents = await getAll(posts_collection)
    return ResponseModel(documents, "List of all posts")

@PostRouter.post("/")
async def create_post(post: Post):
    response = await addOne(posts_collection, post.model_dump())
    return ResponseModel(response, "Post was created")

@PostRouter.get("/{post_id}")
async def read_item(post_id: str):
    item = await getOne(posts_collection, post_id)
    if item:
        return ResponseModel(item, "Found post")
    return ErrorResponseModel("Error occurred", 404, "post does not exist")

@PostRouter.put("/{post_id}")
async def update_item(post_id: str, post: Post):
    updated_post = await updateOne(posts_collection, post_id, post.model_dump())
    if updated_post:
        return ResponseModel({"id": post_id}, "Post sucessfully updated")
    return ErrorResponseModel("Error occurred", 404, "post does not exist")

@PostRouter.delete("/{post_id}")
async def delete_post(post_id: str):
    deleted_post = await deleteOne(posts_collection, post_id)
    if deleted_post:
        return ResponseModel({"id": post_id}, "Post sucessfully deleted")
    return ErrorResponseModel("Error occurred", 404, "post does not exist")
