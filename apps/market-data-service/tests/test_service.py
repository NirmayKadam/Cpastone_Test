from datetime import datetime, timezone

import pytest

from libs.event_schemas import RawTickPayload

from app.services import MarketDataService


class InvalidAdapter:
    async def get_next_tick(self) -> RawTickPayload:
        return RawTickPayload(
            symbol='NIFTY',
            expiry='2026-03-26',
            strike=22500,
            option_type='CE',
            instrument_token='BROKEN',
            spot_price=22482.15,
            last_traded_price=125.0,
            bid_price=126.0,
            ask_price=125.0,
            bid_qty=10,
            ask_qty=5,
            volume=100,
            open_interest=20,
            exchange_timestamp=datetime.now(timezone.utc),
        )


@pytest.mark.asyncio
async def test_poll_once_routes_invalid_payloads_to_dlq() -> None:
    service = MarketDataService(adapter=InvalidAdapter())

    event_id = await service.poll_once()
    dlq_events = await service.backbone.read(service.config.data_stream_dlq_topic)

    assert event_id is None
    assert len(dlq_events) == 1
    assert 'ask_price must be greater than or equal to bid_price' in dlq_events[0]['payload']['error']
