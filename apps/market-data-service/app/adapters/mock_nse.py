from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone

from libs.event_schemas import RawTickPayload


class MockNSEAdapter:
    def __init__(self, payloads: Iterable[dict] | None = None) -> None:
        self._payloads = list(payloads or [self._default_payload()])
        self._index = 0

    async def get_next_tick(self) -> RawTickPayload:
        payload = self._payloads[self._index % len(self._payloads)]
        self._index += 1
        return RawTickPayload.model_validate(payload)

    @staticmethod
    def _default_payload() -> dict:
        return {
            'symbol': 'NIFTY',
            'expiry': '2026-03-26',
            'strike': 22500,
            'option_type': 'CE',
            'instrument_token': 'NIFTY-22500-CE',
            'spot_price': 22482.15,
            'last_traded_price': 152.35,
            'bid_price': 152.25,
            'ask_price': 152.45,
            'bid_qty': 500,
            'ask_qty': 450,
            'volume': 120000,
            'open_interest': 240000,
            'exchange_timestamp': datetime.now(timezone.utc),
            'implied_volatility': 0.142,
        }
