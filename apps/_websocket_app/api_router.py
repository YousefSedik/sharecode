from utils.ConnectionManager import ConnectionManager
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from apps.auth_app.utils import validate_jwt
from fastapi import Depends
from db import get_session
from uuid import UUID
import json
from apps._websocket_app.utils import has_access_to_project


router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/join-project/{project_id}")
async def websocket_endpoint(
    project_id: UUID, websocket: WebSocket, session: AsyncSession = Depends(get_session)
):
    token = websocket.query_params.get("token")
    username = validate_jwt(token)
    has_access, access = await has_access_to_project(
        project_id, token, session, websocket
    )
    if not has_access:
        return
    print("User has access to the project", access)
    await manager.connect(websocket, username, session)
    try:
        print(manager)
        while True:
            obj = await websocket.receive_text()
            try:
                obj = json.loads(obj)
            except json.JSONDecodeError as e:
                print("Received data is not a json object: ", e)
                continue
            print(f"Received obj: {obj}")
            type = obj.get("type", "")
            if type == "file-update":
                print(username)
                await manager.handle_file_update(project_id, websocket, obj, username)
            elif type == "file-rename":
                await manager.handle_file_rename(project_id, websocket, obj, username)
            elif type == "file-delete":
                await manager.handle_file_delete(project_id, websocket, obj, username)
            elif type == "file-create":
                await manager.handle_file_create(project_id, websocket, obj, username)
            elif type == "save-project":
                await manager.handle_save(project_id, session)
            print(manager)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        print("Client disconnected")
