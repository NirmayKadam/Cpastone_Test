from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from libs.event_schemas import (
    Instrument,
    MarketSnapshot,
    NormalizedTickEvent,
    QualityInfo,
    RawTickPayload,
    TimingInfo,
)


def normalize_tick(payload: RawTickPayload, *, trace_id: str | None = None) -> NormalizedTickEvent:
    ingestion_timestamp = datetime.now(timezone.utc)
    latency_ms = max(
        0,
        int((ingestion_timestamp - payload.exchange_timestamp).total_seconds() * 1000),
    )
    quality = QualityInfo(
        is_valid=True,
        anomaly_flags=_detect_anomalies(payload),
    )
    return NormalizedTickEvent(
        trace_id=trace_id or str(uuid4()),
        instrument=Instrument(
            symbol=payload.symbol,
            expiry=payload.expiry,
            strike=payload.strike,
            option_type=payload.option_type,
            instrument_token=payload.instrument_token,
        ),
        market=MarketSnapshot(
            spot_price=payload.spot_price,
            last_traded_price=payload.last_traded_price,
            bid_price=payload.bid_price,
            ask_price=payload.ask_price,
            bid_qty=payload.bid_qty,
            ask_qty=payload.ask_qty,
            volume=payload.volume,
            open_interest=payload.open_interest,
            implied_volatility=payload.implied_volatility,
        ),
        timing=TimingInfo(
            exchange_timestamp=payload.exchange_timestamp,
            ingestion_timestamp=ingestion_timestamp,
            normalization_latency_ms=latency_ms,
        ),
        quality=quality,
    )


def _detect_anomalies(payload: RawTickPayload) -> list[str]:
    anomalies: list[str] = []
    if payload.last_traded_price <= 0:
        anomalies.append('non_positive_last_traded_price')
    if payload.open_interest < 0:
        anomalies.append('negative_open_interest')
    if payload.ask_price == payload.bid_price:
        anomalies.append('zero_spread')
    return anomalies
