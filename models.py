from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Institution(BaseModel):
    name: str = Field(...)
    homepage: str = Field(...)
    country: str = Field(...)
    members : List[str] = Field(...)  

class UpdateInstitutionModel(BaseModel):
    name: Optional[str] = Field(None)
    homepage: Optional[str] = Field(None)

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
    profile_description: Optional[str] = Field(default="")
    skills: Optional[List[str]] = Field(default=[])
    user_type: UserType  = Field(...)
    institution_id: str = Field(...)
    birth_date: str = Field(...)
    posts_id: Optional[List[str]] = Field(default=[])
    comments_id: Optional[List[str]] = Field(default=[])
    liked_posts_id:Optional[List[str]] = Field(default=[])
    follows_id :Optional[List[str]] = Field(default=[])
    followers_id : Optional[List[str]]  = Field(default=[])

class UpdateUserModel(BaseModel): 
    display_name: Optional[str] = Field(None)
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    user_type: Optional[UserType] = Field(None)
    profile_description: Optional[str] = Field(None)
    skills: Optional[List[str]] = Field(None)
    institution_id: Optional[str] = Field(None)
    birth_date: Optional[str] = Field(None)
    posts_id: Optional[List[str]] = Field(None)
    comments_id: Optional[List[str]]  = Field(None)
    liked_posts_id: Optional[List[str]]  = Field(None)
    follows_id :Optional[List[str]]  = Field(None)
    followers_id : Optional[List[str]]   = Field(None)

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
    parent_comment_id: Optional[str] = Field(None)
    content : str = Field(...)
    created_at : datetime  = datetime.now()

class CommentCreate(BaseModel):
    author_id : str = Field(...)
    post_id : str = Field(...)
    parent_comment_id: Optional[str] 
    content : str = Field(...)
    created_at : datetime = datetime.now()




