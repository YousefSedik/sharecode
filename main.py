from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin, ModelView
from db import engine
from models import User, ProjectAccess, Project, File

from apps.auth_app.api_router import router as auth_api_router
from apps.auth_app.router import router as auth_router

from apps._websocket_app.api_router import router as web_socket_api_router
from apps._websocket_app.router import router as web_socket_router

from apps.project_app.router import router as project_router
from apps.project_app.api_router import router as project_api_router

from apps.file_app.router import router as file_router
from apps.file_app.api_router import router as file_api_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_api_router, tags=["Authentication"], prefix="/api")
app.include_router(web_socket_api_router, prefix="/api")
app.include_router(project_api_router, prefix="/api")
app.include_router(file_api_router, prefix="/api")

app.include_router(web_socket_router, include_in_schema=False)
app.include_router(auth_router, include_in_schema=False)
app.include_router(project_router, include_in_schema=False)
app.include_router(file_router, include_in_schema=False)

app.mount(
    "/static", StaticFiles(directory="static"), name="static"
)

admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.first_name, User.last_name]

class ProjectAdmin(ModelView, model=Project):
    column_list = [Project.id, Project.name, Project.description]

class FileAdmin(ModelView, model=File):
    column_list = [File.id, File.name, File.created_at, File.updated_at]
class ProjectAccessAdmin(ModelView, model=ProjectAccess):
    column_list = [ProjectAccess.id, ProjectAccess.project_id, ProjectAccess.type, ProjectAccess.user_id]

admin.add_view(UserAdmin)
admin.add_view(ProjectAdmin)
admin.add_view(ProjectAccessAdmin)
admin.add_view(FileAdmin)

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "https://sharecode-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
