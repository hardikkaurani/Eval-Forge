from typing import Dict, Set
from fastapi import WebSocket

class WebSocketManager:
    """Manages active WebSocket connections for real-time progress updates and notification events."""

    def __init__(self) -> None:
        # Maps job_id to connected client sockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Maps project_id to connected client sockets
        self.project_connections: Dict[str, Set[WebSocket]] = {}

    async def connect_job(self, job_id: str, websocket: WebSocket) -> None:
        """Accepts a WebSocket connection and registers it for updates on a specific job ID."""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)

    async def connect_project(self, project_id: str, websocket: WebSocket) -> None:
        """Accepts a WebSocket connection and registers it for updates on a project level."""
        await websocket.accept()
        if project_id not in self.project_connections:
            self.project_connections[project_id] = set()
        self.project_connections[project_id].add(websocket)

    def disconnect_job(self, job_id: str, websocket: WebSocket) -> None:
        """Removes a client connection from a job subscription."""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    def disconnect_project(self, project_id: str, websocket: WebSocket) -> None:
        """Removes a client connection from a project subscription."""
        if project_id in self.project_connections:
            self.project_connections[project_id].discard(websocket)
            if not self.project_connections[project_id]:
                del self.project_connections[project_id]

    async def broadcast_job_update(self, job_id: str, data: dict) -> None:
        """Sends JSON updates to all clients subscribed to a specific job ID."""
        if job_id in self.active_connections:
            for connection in list(self.active_connections[job_id]):
                try:
                    await connection.send_json(data)
                except Exception:
                    self.disconnect_job(job_id, connection)

    async def broadcast_project_update(self, project_id: str, data: dict) -> None:
        """Sends JSON updates to all clients subscribed to a specific project ID."""
        if project_id in self.project_connections:
            for connection in list(self.project_connections[project_id]):
                try:
                    await connection.send_json(data)
                except Exception:
                    self.disconnect_project(project_id, connection)


websocket_manager = WebSocketManager()
