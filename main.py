from fastapi import FastAPI

from colleges_service import CollegeRouter
from users_service import UserRouter
from posts_service import PostRouter
from comments_service import CommentRouter
from categories_service import CategoryRouter

app = FastAPI()
app.include_router(CollegeRouter, tags=["College"], prefix="/college")
app.include_router(UserRouter, tags=["User"], prefix="/user")
app.include_router(PostRouter, tags=["Post"], prefix="/post")
app.include_router(CommentRouter, tags=["Comment"], prefix="/comment")
app.include_router(CategoryRouter, tags=["Category"], prefix="/category")
