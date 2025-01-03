from fastapi import WebSocket
from uuid import UUID

class ConnectionManager:
    def __init__(self):
        self.project_connected_users: dict[UUID: list[list[WebSocket, str]]] = {}
    
    async def connect(self, websocket: WebSocket, username: str):
        """
        Accepts the WebSocket connection, retrieves user details from query parameters,
        and adds the connection to the active connections dictionary.
        """
        await websocket.accept()
        try:
            project_id = UUID(websocket.path_params.get("project_id"))
            if project_id not in self.project_connected_users:
                self.project_connected_users[project_id] = [[websocket, username]]
            else:
                self.project_connected_users[project_id].append([websocket, username])
            
            print(f"New connection: username={username}")
        except ValueError:
            await websocket.close()
            return

    def disconnect(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active connections dictionary.
        """

        if websocket in self.active_connections:
            username, device_type = self.active_connections[websocket]
            del self.active_connections[websocket]
            self.active_connections_usernames[username].remove(device_type)
            print(f"Disconnected: {websocket}")

    async def number_of_connected_users(self, project_id):
        return len(self.project_connected_users.get(project_id))

    def __str__(self) -> str:
        result = ""
        for project_id, li in self.project_connected_users.items():
            result += f"project_id: {project_id}\n"
            for ws, username in li:
                result += f"username: {username}\n"
            
        return result
