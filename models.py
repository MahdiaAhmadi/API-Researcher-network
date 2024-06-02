from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Institution(BaseModel):
    name: str = Field(...)
    homepage: str = Field(...)
    country: str = Field(...)
    members : List[str] = Field(...)  

class UpdateInstitutionModel(BaseModel):
    name: Optional[str] = Field(...)
    homepage: Optional[str] = Field(...)

class UserType(BaseModel):
    code: int = Field(...)
    type: str = Field(...)

class LoginUser(BaseModel):
    username: str 
    password: str 

class AccountCreate(BaseModel):
    display_name: str = Field(...)
    email: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    institution_id: str = Field(...)
    birth_date: str = Field(...)

class User(BaseModel): 
    display_name: str = Field(...)
    email: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    profile_description: Optional[str] = Field(...)
    user_type: Optional[UserType]  = Field(...)
    institution_id: str = Field(...)
    birth_date: str = Field(...)
    posts_id: Optional[List[str]] = Field(...)
    comments_id: Optional[List[str]] = Field(...)
    liked_posts_id:Optional[List[str]] = Field(...)
    follows_id :Optional[List[str]] = Field(...)
    followers_id : Optional[List[str]]  = Field(...)

class UpdateUserModel(BaseModel): 
    display_name: Optional[str] = Field(...)
    username: Optional[str] = Field(...)
    password: Optional[str] = Field(...)
    user_type: Optional[UserType] = Field(...)
    institution_id: Optional[str] = Field(...)
    birth_date: Optional[str] = Field(...)
    posts_id: Optional[List[str]] = Field(...)
    comments_id: Optional[List[str]]  = Field(...)
    liked_posts_id: Optional[List[str]]  = Field(...)
    follows_id :Optional[List[str]]  = Field(...)
    followers_id : Optional[List[str]]   = Field(...)

class Post(BaseModel):
    title:str = Field(...)
    categories_id: List[str] = Field(...) 
    likes:int = Field(...)
    author_id: str = Field(...) 
    summary: str = Field(...)
    content: str = Field(...) 
    comments_id: List[str] = Field(...) 
    research_link: str = Field(...)
    visibility : int = Field(...)
    file_path: str = Field(...)
    created_at : datetime  = datetime.now()


class Category(BaseModel):
    name:str = Field(...)
    posts_id: List[str] = Field(...)

class CommentList(BaseModel):
    author_id : str = Field(...)
    post_id : str = Field(...)
    parent_comment_id: Optional[str] = Field(...)
    content : str = Field(...)
    created_at : datetime  = datetime.now()

class CommentCreate(BaseModel):
    author_id : str = Field(...)
    post_id : str = Field(...)
    parent_comment_id: Optional[str] = Field(...)
    content : str = Field(...)
    created_at : datetime  = datetime.now()




