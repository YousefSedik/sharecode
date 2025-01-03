from fastapi.testclient import TestClient
from main import app
from fastapi import WebSocket
from fastapi.testclient import TestWebSocket
from fastapi import WebSocketDisconnect
import json

client = TestClient(app)
def test_websocket():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello WebSocket!")
        data = websocket.receive_text()
        assert data == "Echo: Hello WebSocket!"
