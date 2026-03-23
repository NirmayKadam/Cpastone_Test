from __future__ import annotations

from collections import defaultdict
from typing import Any


class InMemoryEventBackbone:
    def __init__(self) -> None:
        self._streams: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def publish(self, topic: str, payload: dict[str, Any]) -> str:
        stream = self._streams[topic]
        event_id = f'{len(stream) + 1}-0'
        stream.append({'id': event_id, 'payload': payload})
        return event_id

    async def read(self, topic: str) -> list[dict[str, Any]]:
        return list(self._streams[topic])
