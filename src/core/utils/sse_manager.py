import asyncio
import uuid
from collections import defaultdict
from typing import AsyncGenerator

class SSEManager:
    def __init__(self):
        self._connections: dict[int, dict[str, asyncio.Queue]] = defaultdict(dict)

    def connect(self, staff_id: int) -> tuple[str, asyncio.Queue]:
        conn_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue()
        self._connections[staff_id][conn_id] = queue
        return conn_id, queue

    def disconnect(self, staff_id: int, conn_id: str) -> None:
        conns = self._connections.get(staff_id, {})
        conns.pop(conn_id, None)
        if not conns:
            self._connections.pop(staff_id, None)

    async def send(self, staff_id: int, data: dict) -> bool:
        conns = self._connections.get(staff_id, {})
        if not conns:
            return False
        for queue in conns.values():
            await queue.put(data)
        return True

    async def stream(
        self, staff_id: int, conn_id: str, queue: asyncio.Queue
    ) -> AsyncGenerator[dict, None]:
        try:
            while True:
                data = await queue.get()
                yield data
        except asyncio.CancelledError:
            pass
        finally:
            self.disconnect(staff_id, conn_id)

sse_manager = SSEManager()