from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from categories_service import CategoryRouter
from comments_service import CommentRouter
from institutions_service import InstitutionRouter
from posts_service import PostRouter
from users_service import UserRouter

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
