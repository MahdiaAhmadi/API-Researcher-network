from fastapi import FastAPI

from colleges_service import CollegeRouter
from users_service import UserRouter

app = FastAPI()
app.include_router(CollegeRouter, tags=["College"], prefix="/college")
app.include_router(UserRouter, tags=["User"], prefix="/user")
