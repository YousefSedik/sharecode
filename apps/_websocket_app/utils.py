from sqlalchemy import select, and_
from models import User, Project, ProjectAccess
from apps.auth_app.utils import validate_jwt


async def has_access_to_project(project_id, token, session, websocket):
    if token is None:
        await websocket.close()
        return False, None
    username = validate_jwt(token)
    user = await session.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    project = await session.get(Project, project_id)
    access = None
    if project is None:
        await websocket.close()
        return False, None
    else:
        if project.owner_id == user.id:
            access = "owner"
        else:
            result = await session.execute(
                select(ProjectAccess).where(
                    and_(
                        ProjectAccess.project_id == project_id,
                        ProjectAccess.user_id == user.id,
                    )
                )
            )
            project_access = result.scalars().first()
            if project_access is None:
                await websocket.close()
                return
            elif project_access.type == "VIEW":
                access = "view"
            elif project_access.type == "FULL_ACCESS":
                access = "read/write"

        if access is None:
            await websocket.close()
            return False, None

    return True, access
