from utils.ConnectionManager import ConnectionManager
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from models import User, Project, ProjectAccess, File
from sqlmodel import select
from apps.auth_app.utils import validate_jwt
from fastapi import Depends
from fastapi import HTTPException
from db import get_session
from uuid import UUID
import json

# import and_
from sqlalchemy import and_, or_

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/join-project/{project_id}")
async def websocket_endpoint(
    project_id: UUID, websocket: WebSocket, session: AsyncSession = Depends(get_session)
):
    token = websocket.query_params.get("token")
    if token is None:
        print("Token is missing")
        await websocket.close()
        return
    username = validate_jwt(token)
    user = await session.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    project = await session.get(Project, project_id)
    access = None
    if project is None:
        print("Project not found")
        await websocket.close()
        return
    else:
        if project.owner_id == user.id:
            access = "owner"
        else:
            result = await session.execute(
                select(ProjectAccess).where(
                    and_(
                        ProjectAccess.project_id == project_id,
                        ProjectAccess.user_id == user.id
                    )
                )
            )
            project_access = result.scalars().first()
            if project_access is None:
                print("User has no access to the project")
                await websocket.close()
                return
            elif project_access.type == "VIEW":
                access = "view"
            elif project_access.type == "FULL_ACCESS":
                access = "read/write"

        if access is None:
            print("User has no access to the project")
            await websocket.close()
            return

    await manager.connect(websocket, username)
    # get project files
    if await manager.number_of_connected_users(project_id) == 1:

        result = await session.execute(select(File).where(File.project_id == project_id))    
    else:
        pass
    try:
        while True:
            obj = await websocket.receive_text()
            try:
                obj = json.loads(obj)
            except json.JSONDecodeError as e:
                print("Received data is not a json object: ", e)
                continue

            print(f"Received obj: {obj}")
            print(manager)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
