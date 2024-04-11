from fastapi import FastAPI

from colleges_service import CollegeRouter

app = FastAPI()
app.include_router(CollegeRouter, tags=["College"], prefix="/college")