from fastapi import FastAPI

from institutions_service import InstitutionRouter
from users_service import UserRouter
from posts_service import PostRouter
from comments_service import CommentRouter
from categories_service import CategoryRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(InstitutionRouter, tags=["Institution"], prefix="/institution")
app.include_router(UserRouter, tags=["User"], prefix="/user")
app.include_router(PostRouter, tags=["Post"], prefix="/post")
app.include_router(CommentRouter, tags=["Comment"], prefix="/comment")
app.include_router(CategoryRouter, tags=["Category"], prefix="/category")
