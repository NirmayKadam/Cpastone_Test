from datetime import datetime, timezone

from libs.event_schemas import RawTickPayload

from app.pipelines.normalizer import normalize_tick


def test_normalize_tick_maps_raw_payload() -> None:
    payload = RawTickPayload(
        symbol='NIFTY',
        expiry='2026-03-26',
        strike=22500,
        option_type='CE',
        instrument_token='NIFTY-22500-CE',
        spot_price=22482.15,
        last_traded_price=152.35,
        bid_price=152.25,
        ask_price=152.45,
        bid_qty=500,
        ask_qty=450,
        volume=120000,
        open_interest=240000,
        exchange_timestamp=datetime.now(timezone.utc),
        implied_volatility=0.142,
    )

    normalized = normalize_tick(payload, trace_id='trace-123')

    assert normalized.instrument.symbol == 'NIFTY'
    assert normalized.instrument.option_type == 'CE'
    assert normalized.trace_id == 'trace-123'
    assert normalized.market.open_interest == 240000
    assert normalized.quality.is_valid is True


def test_normalize_tick_generates_trace_id_when_missing() -> None:
    payload = RawTickPayload(
        symbol='NIFTY',
        expiry='2026-03-26',
        strike=22500,
        option_type='PE',
        instrument_token='NIFTY-22500-PE',
        spot_price=22482.15,
        last_traded_price=99.10,
        bid_price=99.0,
        ask_price=99.2,
        bid_qty=250,
        ask_qty=275,
        volume=50000,
        open_interest=125000,
        exchange_timestamp=datetime.now(timezone.utc),
    )

    normalized = normalize_tick(payload)

    assert normalized.trace_id
