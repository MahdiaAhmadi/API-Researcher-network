from typing import Optional

from pydantic import BaseModel, Field


class CollegeSchema(BaseModel):
    name: str = Field(...)
    homepage: str = Field(...)


class UpdateCollegeModel(BaseModel):
    name: Optional[str] = Field(...)
    homepage: Optional[str] = Field(...)