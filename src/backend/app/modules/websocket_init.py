from typing import Dict, List
from fastapi import WebSocket

# class WebSocketManager:
#     def __init__(self):
#         # Structure: { user_id: { session_id: { thread_id: [WebSocket, ...] } } }
#         self.connections: Dict[str, Dict[str, Dict[str, List[WebSocket]]]] = {}

#     async def connect(self, user_id: str, session_id: str, thread_id: str, websocket: WebSocket):
#         self.connections.setdefault(user_id, {}).setdefault(session_id, {}).setdefault(thread_id, []).append(websocket)

#     def disconnect(self, user_id: str, session_id: str, thread_id: str, websocket: WebSocket):
#         try:
#             self.connections[user_id][session_id][thread_id].remove(websocket)
#             if not self.connections[user_id][session_id][thread_id]:
#                 del self.connections[user_id][session_id][thread_id]
#             if not self.connections[user_id][session_id]:
#                 del self.connections[user_id][session_id]
#             if not self.connections[user_id]:
#                 del self.connections[user_id]
#         except (KeyError, ValueError):
#             pass

#     async def send_to_session(self, user_id: str, session_id: str, thread_id: str, message: str):
#         """Send message to a specific session only."""
#         try:
#             websockets = self.connections[user_id][session_id][thread_id]
#             for ws in websockets:
#                 await ws.send_text(message)
#         except KeyError:
#             pass


#     async def broadcast_to_all_sessions(self, user_id: str, message: str):
#         """Broadcast a message to all sessions of the user (e.g., new thread)."""
#         user_sessions = self.connections.get(user_id, {})
#         for session_id in user_sessions:
#             for thread_ws_list in user_sessions[session_id].values():
#                 for ws in thread_ws_list:
#                     await ws.send_text(message)
class WebSocketManager:
    def __init__(self):
        # { user_id: { session_id: { "websocket": ws, "thread_id": str } } }
        self.connections: Dict[str, Dict[str, Dict[str, any]]] = {}

    async def connect(self, user_id: str, session_id: str, websocket: WebSocket):
        self.connections.setdefault(user_id, {})[session_id] = {
            "websocket": websocket,
            "thread_id": None,
        }

    def set_thread(self, user_id: str, session_id: str, thread_id: str):
        if user_id in self.connections and session_id in self.connections[user_id]:
            self.connections[user_id][session_id]["thread_id"] = thread_id

    def get_thread(self, user_id: str, session_id: str) -> str:
        return self.connections.get(user_id, {}).get(session_id, {}).get("thread_id")

    def disconnect(self, user_id: str, session_id: str):
        self.connections.get(user_id, {}).pop(session_id, None)
        if not self.connections[user_id]:
            self.connections.pop(user_id)

    async def send_to_current_thread(self, user_id: str, session_id: str, message: str):
        conn = self.connections.get(user_id, {}).get(session_id)
        if conn and conn["thread_id"]:
            await conn["websocket"].send_text(message)

    async def broadcast_to_all_sessions(self, user_id: str, message: str):
        for conn in self.connections.get(user_id, {}).values():
            await conn["websocket"].send_text(message)
