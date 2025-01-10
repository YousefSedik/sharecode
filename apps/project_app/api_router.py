from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status, Response
from apps.auth_app.utils import get_current_user
from db import get_session
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import Project, User, ProjectAccess
from .schemas import (
    CreateProject,
    UpdateAccessProject,
    DeleteAccessProject,
    GrantAccessProject,
    UpdateProject,
    ProjectResponse,
)
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import and_, or_, case
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.post("/project")
async def create_project(
    project: CreateProject,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_project = Project(
        name=project.name, description=project.description, owner_id=current_user.id
    )
    session.add(new_project)
    await session.flush()

    if project.access_list:
        for access in project.access_list:
            project_access = ProjectAccess(
                user_id=int(access.user_id),
                type=access.access_level,
                project_id=new_project.id,
            )
            session.add(project_access)

    await session.commit()  # Commit at the end
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/project")
async def get_project_list(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    

    result = await session.execute(
    select(
        Project.id,
        Project.description,
        Project.name,
        Project.created_at,
        Project.updated_at,
        case(
            *[
                (Project.owner_id == current_user.id, "Owner"),
                (
                    Project.access_list.any(and_(ProjectAccess.user_id == current_user.id, ProjectAccess.type == "FULL_ACCESS")),
                    "Read/Write",
                ),
                (
                    Project.access_list.any(and_(ProjectAccess.user_id == current_user.id, ProjectAccess.type == "VIEW")),
                    "Read",
                ),
            ],
            else_="Unknown"  # Optional, defaults to "Unknown" if none of the conditions match
        ).label("type")
    ).where(
        or_(
            Project.owner_id == current_user.id,
            Project.access_list.any(user_id=current_user.id),
        )
    )
    .order_by(Project.updated_at.desc())
)
    projects = result.mappings().all()
    return projects


@router.delete("/project/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if project:
        if project.owner_id == current_user.id:
            await session.delete(project)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@router.put("/project/{project_id}")
async def update_project(
    project_id: str,
    access: UpdateProject,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if project:
        if project.owner_id == current_user.id:
            if access.name != project.name or access.description != project.description:
                project.updated_at = datetime.now()
                project.name = access.name
                project.description = access.description
                await session.commit()
                await session.refresh(project)
            return project.model_dump(exclude=["owner_id", "created_at", "updated_at"])
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/project/{project_id}", response_model=ProjectResponse)
async def get_project_details(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Query to fetch project and related data
    query = (
        select(Project)
        .options(
            joinedload(Project.access_list).joinedload(
                ProjectAccess.user
            ),  # Join User for access_list
            joinedload(Project.files),  # Eager load files
        )
        .where(
            or_(
                Project.owner_id == current_user.id,  # Check if user is the owner
                Project.access_list.any(
                    user_id=current_user.id
                ),  # Check if user has access
            ),
            Project.id == project_id,
        )
    )

    result = await session.execute(query)
    project = result.scalars().first()

    # Ensure project exists
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    access_level = None
    # Transform access_list to include `username`
    access_list_with_usernames = []
    for access in project.access_list:
        if access.user_id == current_user.id:
            if access.type == "FULL_ACCESS":
                access_level = "Read/Write"
            elif access.type == "VIEW":
                access_level = "Read"
        
        access_list_with_usernames.append(
            {
                "id": access.id,
                "user_id": access.user_id,
                "username": access.user.username,  # Fetch username from the related User
                "type": access.type,
            }
        )

    # Transform files
    files = [
        {
            "id": file.id,
            "name": file.name,
            "created_at": str(file.created_at),
            "updated_at": str(file.updated_at),
        }
        for file in project.files
    ]
    if access_level is None:
        access_level = "Owner"
    
    # Construct the response
    project_response = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "access_type": access_level,
        "access_list": access_list_with_usernames,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "files": files,
    }
    project_response = ProjectResponse(**project_response)
    return project_response


@router.post("/project/{project_id}/access")
async def grant_access(
    project_id: str,
    access: GrantAccessProject,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user_id = access.user_id
    access_level = access.access_level

    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="You can't grant access to yourself"
        )

    project_access = ProjectAccess(
        user_id=user_id, type=access_level, project_id=project.id
    )
    print(project_access)
    session.add(project_access)
    try:
        await session.commit()
    except IntegrityError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Access already granted")

    await session.refresh(project_access)
    return project_access.model_dump()


@router.delete("/project/{project_id}/access")
async def delete_access(
    project_id: str,
    access: DeleteAccessProject,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if project:
        if project.owner_id == current_user.id:
            project_access = await session.get(ProjectAccess, access.access_id)
            if project_access:
                await session.delete(project_access)
                await session.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            else:
                raise HTTPException(status_code=404, detail="Access not found")
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@router.put("/project/{project_id}/access")
async def update_access(
    project_id: str,
    access: UpdateAccessProject,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):

    project = await session.get(Project, project_id)
    if project:
        if project.owner_id == current_user.id:
            project_access = await session.get(ProjectAccess, access.access_id)
            if project_access:
                project_access.type = access.access_level
                await session.commit()
                await session.refresh(project_access)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            else:
                raise HTTPException(status_code=404, detail="Access not found")
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/project/{project_id}/access")
async def get_access(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if project:
        result = await session.execute(
            select(ProjectAccess).where(ProjectAccess.project_id == project_id)
        )
        accesses = result.scalars().all()
        if current_user.id in [access.user_id for access in accesses] + [project.owner_id]:
            print(accesses)
            return accesses
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="Project not found")
