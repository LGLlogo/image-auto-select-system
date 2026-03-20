class WSManager:

    def __init__(self):
        self.rooms = {}  # task_id -> [websocket]

    async def connect(self, task_id, websocket):
        await websocket.accept()
        self.rooms.setdefault(task_id, []).append(websocket)

    def disconnect(self, task_id, websocket):
        if task_id in self.rooms:
            self.rooms[task_id].remove(websocket)

    async def broadcast(self, task_id, data):
        if task_id not in self.rooms:
            return

        for ws in self.rooms[task_id]:
            await ws.send_json(data)


ws_manager = WSManager()
