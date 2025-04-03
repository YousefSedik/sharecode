from fastapi import WebSocket
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import File as FileModel
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        # project_id: [[WebSocket, username]]
        self.project_connected_users: dict[UUID : list[list[WebSocket, str]]] = {}
        # project_id: [{name: str, text: str, timestamp: int}]
        self.project_data: dict[UUID : list[dict]] = defaultdict(lambda: [])
        # file_id: usernames
        self.viewing_files: dict[str : list[str]] = defaultdict(lambda: [])

    async def connect(self, websocket: WebSocket, username: str, session: AsyncSession):
        """
        Accepts the WebSocket connection, retrieves user details from query parameters,
        and adds the connection to the active connections dictionary.
        """
        await websocket.accept()
        try:
            project_id = UUID(websocket.path_params.get("project_id"))
            if project_id not in self.project_connected_users:  # first connection
                self.project_connected_users[project_id] = [[websocket, username]]
                await self.init_project_files(project_id, session)
                await self.send_project_files(project_id, websocket)
            else:
                await self.send_project_files(project_id, websocket)
                await self.broadcast(
                    project_id, {"type": "user-joined", "username": username}, username
                )
                self.project_connected_users[project_id].append([websocket, username])

            await self.broadcast(
                project_id,
                {
                    "type": "joined-users",
                    "usernames": [
                        user[1] for user in self.project_connected_users[project_id]
                    ],
                },
            )

            print(f"New connection: username={username}")
        except ValueError:
            await websocket.close()
            return

    async def disconnect(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active connections dictionary.
        """

        for project_id, li in self.project_connected_users.items():
            save_ws, save_username = None, None
            for ws, username in li:
                if ws == websocket:
                    save_ws = ws
                    save_username = username
                    print(f"Disconnected: {websocket}")
                    await self.broadcast(
                        project_id,
                        {"type": "user-left", "username": username},
                        username,
                    )
            if all([save_ws, save_username]):
                print("deleting user", save_username)
                li.remove([save_ws, save_username])
                if len(li) == 0:
                    print("deleting project", project_id)
                    del self.project_connected_users[project_id]
                break

    async def notify(self, websocket: WebSocket, message: dict):
        """
        Sends a message to a specific WebSocket connection.
        """
        await websocket.send_json(message)

    async def number_of_connected_users(self, project_id):
        return len(self.project_connected_users.get(project_id))

    async def handle_file_rename(
        self, project_id: UUID, websocket: WebSocket, data: dict, sender=None
    ):
        await self.rename_file(project_id, data.get("old_name"), data.get("new_name"))
        await self.broadcast(project_id, data)
        print(self.project_data.get(project_id))

    async def handle_file_delete(
        self, project_id: UUID, websocket: WebSocket, data: dict, sender=None
    ):
        await self.delete_file(project_id, data.get("file_name"))
        await self.broadcast(project_id, data)
        print(self.project_data.get(project_id))

    async def handle_file_create(
        self, project_id: UUID, websocket: WebSocket, data: dict, sender=None
    ):
        await self.create_file(
            project_id, data.get("file_name"), data.get("file_content")
        )
        await self.broadcast(project_id, data)
        print(self.project_data.get(project_id))

    async def create_file(self, project_id: UUID, file_name: str, file_content: str):
        files = self.project_data.get(project_id)
        files.append({"name": file_name, "text": file_content, "timestamp": 0})
        print(f"Created file: {file_name}")

    async def rename_file(self, project_id: UUID, old_name: str, new_name: str):
        files = self.project_data.get(project_id)
        for file in files:
            if file["name"] == old_name:
                file["name"] = new_name
                break

    async def delete_file(self, project_id: UUID, file_name: str):
        files = self.project_data.get(project_id)
        for file in files:
            if file["name"] == file_name:
                files.remove(file)
                break

    async def init_project_files(self, project_id: UUID, session: AsyncSession):
        # get project files
        print("init_project files")
        files = await session.execute(
            select(FileModel).where(FileModel.project_id == project_id)
        )
        files_objects = files.scalars().all()
        files = []
        for file in files_objects:
            files.append(
                {
                    "name": file.name,
                    "text": file.text,
                    "timestamp": file.updated_at.timestamp() / 1000,
                    "id": file.id,
                }
            )
        self.project_data[project_id] = files
        print(f"project files: {files}")

    async def send_project_files(self, project_id: UUID, websocket: WebSocket):
        message = {"type": "init-files", "files": []}
        files = self.project_data.get(project_id)

        print(f"Sending files: {files}")
        for file in files:
            message["files"].append(
                {
                    "name": file["name"],
                    "content": file["text"],
                }
            )

        await websocket.send_json(message)

    async def handle_file_update(
        self, project_id: UUID, websocket: WebSocket, data: dict, sender=None
    ):
        file_name = data.get("file_name")
        new_content = data.get("content")
        timestamp = data.get("timestamp")
        # Check if the new content is too long (more than 500 lines)
        if len(new_content.split("\n")) >= 500:
            message = {
                "type": "file-update-error",
                "file_name": file_name,
                "error": "File content is too long",
                "timestamp": timestamp,
            }

            await self.broadcast(project_id, message, sender, send_to_all=True)
            return
        print(f"Received file update: {file_name}")
        print(f"New content: {type(new_content)}")
        print(f"Timestamp: {timestamp}")
        # Update the file content in the project data
        files = self.project_data.get(project_id)
        for file in files:
            if file["name"] == file_name:
                print(files)
                if (
                    (timestamp and timestamp > file["timestamp"]) or not timestamp
                ):  # Only update if the new change is more recent
                    file["text"] = new_content
                    file["timestamp"] = timestamp

                break

        # Broadcast the update to all connected clients
        message = {
            "type": "file-update",
            "file_name": file_name,
            "content": new_content,
            "timestamp": timestamp,
        }

        await self.broadcast(project_id, message, sender)

    async def handle_save(self, project_id: UUID, session: AsyncSession):
        # get project files
        files = self.project_data.get(project_id)
        files_objects = await session.execute(
            select(FileModel).where(FileModel.project_id == project_id)
        )
        files_objects = files_objects.scalars().all()
        for file_data in files:
            if file_data.get("id") is None:  # create the file
                file = FileModel(
                    name=file_data["name"],
                    text=file_data["text"] or "",
                    project_id=project_id,
                )
                session.add(file)
            else:
                for file in files_objects:
                    if file.id == file_data["id"]:  # update the file
                        file.text = file_data["text"]
                        file.name = file_data["name"]
                        break
        for file in files_objects:
            if file.id is not None and not any(
                [f.get("id", "-1") == file.id for f in files]
            ):
                await session.delete(file)

        await session.commit()

        print("Project saved")

    async def broadcast(self, project_id: UUID, message: dict, sender=None, send_to_all=False):
        """
        Sends a message to all WebSocket connections.
        """
        print(f"Broadcasting: {message}")
        for ws, username in self.project_connected_users.get(project_id, [None, None]):
            if sender is not None and username == sender and not send_to_all:
                continue
            await ws.send_json(message)

    def __str__(self) -> str:
        result = "Connection manager:"
        for project_id, li in self.project_connected_users.items():
            result += f"project_id: {project_id}\n"
            for ws, username in li:
                result += f"- username: {username}\n"

        return result
