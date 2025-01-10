from pydantic import BaseModel, Field, EmailStr
from pydantic import field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class CreateProjectAccessList(BaseModel):
    user_id: int = Field(..., title="User Id")
    username: str = Field(..., title="Username")
    access_level: str = Field(..., title="Access level")

class CreateProject(BaseModel):
    name: str = Field(..., title="Project name")
    description: str = Field(..., title="Project description")
    access_list: List[CreateProjectAccessList] = []

class UpdateProject(BaseModel):
    name: str = Field(..., title="Project name")
    description: str = Field(..., title="Project description")

class GrantAccessProject(BaseModel):
    user_id: int = Field(..., title="User ID")
    access_level: str = Field(..., title="Access level")

    @field_validator("access_level")
    @classmethod
    def validate_access(cls, value):
        if value not in ["VIEW", "FULL_ACCESS"]:
            raise ValueError("Invalid access level")
        return value

class UpdateAccessProject(BaseModel):
    access_id: UUID = Field(..., title="Access ID")
    access_level: str = Field(..., title="Access level")
    
    @field_validator("access_level")
    @classmethod
    def validate_access(cls, value):
        if value not in ["VIEW", "FULL_ACCESS"]:
            raise ValueError("Invalid access level")
        return value


class DeleteAccessProject(BaseModel):
    access_id: UUID = Field(..., title="Access ID")

class FileResponse(BaseModel):
    id: UUID
    name: str
    created_at: str
    updated_at: str


class ProjectAccessResponse(BaseModel):
    id: UUID
    user_id: int
    username: str
    type: str


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    access_type: str
    access_list: List[ProjectAccessResponse] = []
    files: List[FileResponse] = []

    class Config:
        from_attributes = True
