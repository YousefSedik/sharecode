from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel
from typing import Optional
from sqlmodel import Relationship
from datetime import datetime
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    first_name: str
    last_name: str
    password: str

    # Relationships
    owned_projects: list["Project"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    project_access: list["ProjectAccess"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    def __str__(self):
        return self.username


class Project(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", nullable=False)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: User = Relationship(back_populates="owned_projects")
    files: list["File"] = Relationship(back_populates="project", cascade_delete=True)
    access_list: list["ProjectAccess"] = Relationship(
        back_populates="project", cascade_delete=True
    )


class ProjectAccess(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(
        foreign_key="user.id", nullable=False
    )  
    project_id: UUID = Field(foreign_key="project.id", nullable=False)
    type: str  # "VIEW" or "FULL_ACCESS"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # user_id and project_id are unique together

    __table_args__ = (
        CheckConstraint("type IN ('VIEW', 'FULL_ACCESS')"),
        UniqueConstraint("user_id", "project_id", name="unique_user_project"),
    )

    # Relationships
    user: "User" = Relationship(
        back_populates="project_access"
    )  # noqa: F821
    project: "Project" = Relationship(back_populates="access_list")


class File(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id", nullable=False)
    name: str
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="files")
