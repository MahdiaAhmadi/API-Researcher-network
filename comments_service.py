from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter

from models import CommentCreate
from helpers import ErrorResponseModel, ResponseModel, addOne, deleteOne, getAll, getOne, updateOne

MONGO_URL = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["research_network"]
comments_collection = database["comments"]

CommentRouter = APIRouter()

@CommentRouter.get("/")
async def list_comments():
    documents = await getAll(comments_collection)
    return ResponseModel(documents, "List of all comments")

@CommentRouter.post("/")
async def create_comment(comment: CommentCreate):
    response = await addOne(comments_collection, comment.model_dump())
    return ResponseModel(response, "Comment was created")

@CommentRouter.get("/{comment_id}")
async def read_comment(comment_id: str):
    item = await getOne(comments_collection, comment_id)
    if item:
        return ResponseModel(item, "Found comment")
    return ErrorResponseModel("Error occurred", 404, "comment does not exist")

@CommentRouter.put("/{comment_id}")
async def update_comment(comment_id: str, comment: CommentCreate):
    updated_comment = await updateOne(comments_collection, comment_id, comment.model_dump())
    if updated_comment:
        return ResponseModel({"id": comment_id}, "Comment sucessfully updated")
    return ErrorResponseModel("Error occurred", 404, "comment does not exist")

@CommentRouter.delete("/{comment_id}")
async def delete_comment(comment_id: str):
    deleted_comment = await deleteOne(comments_collection, comment_id)
    if deleted_comment:
        return ResponseModel({"id": comment_id}, "Comment sucessfully deleted")
    return ErrorResponseModel("Error occurred", 404, "comment does not exist")
