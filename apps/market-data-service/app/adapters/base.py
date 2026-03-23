from __future__ import annotations

from typing import Protocol

from libs.event_schemas import RawTickPayload


class MarketDataAdapter(Protocol):
    async def get_next_tick(self) -> RawTickPayload:
        ...
