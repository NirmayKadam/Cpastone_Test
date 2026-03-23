from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class Instrument(BaseModel):
    symbol: str
    expiry: str
    strike: float
    option_type: str
    instrument_token: str

    @field_validator('option_type')
    @classmethod
    def validate_option_type(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {'CE', 'PE'}:
            raise ValueError('option_type must be CE or PE')
        return normalized


class MarketSnapshot(BaseModel):
    spot_price: float
    last_traded_price: float
    bid_price: float
    ask_price: float
    bid_qty: int
    ask_qty: int
    volume: int
    open_interest: int
    implied_volatility: float | None = None

    @model_validator(mode='after')
    def validate_spread(self) -> 'MarketSnapshot':
        if self.ask_price < self.bid_price:
            raise ValueError('ask_price must be greater than or equal to bid_price')
        return self


class TimingInfo(BaseModel):
    exchange_timestamp: datetime
    ingestion_timestamp: datetime
    normalization_latency_ms: int = Field(ge=0)


class QualityInfo(BaseModel):
    is_valid: bool = True
    dropped_fields: list[str] = Field(default_factory=list)
    anomaly_flags: list[str] = Field(default_factory=list)


class NormalizedTickEvent(BaseModel):
    schema_version: str = '1.0.0'
    event_type: str = 'market.tick.normalized'
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str = 'nse.websocket'
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    instrument: Instrument
    market: MarketSnapshot
    timing: TimingInfo
    quality: QualityInfo = Field(default_factory=QualityInfo)

    def stream_payload(self) -> dict[str, Any]:
        return self.model_dump(mode='json')


class RawTickPayload(BaseModel):
    symbol: str
    expiry: str
    strike: float
    option_type: str
    instrument_token: str
    spot_price: float
    last_traded_price: float
    bid_price: float
    ask_price: float
    bid_qty: int
    ask_qty: int
    volume: int
    open_interest: int
    exchange_timestamp: datetime
    implied_volatility: float | None = None


class StreamCommand(BaseModel):
    action: str

    @field_validator('action')
    @classmethod
    def validate_action(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {'start', 'stop'}:
            raise ValueError('action must be start or stop')
        return normalized


class PreprocessingJobRequest(BaseModel):
    source: str = 'api'
    replay_from: datetime | None = None
    replay_to: datetime | None = None
    batch_size: int = Field(default=500, ge=1, le=10_000)


class JobStatus(BaseModel):
    job_id: str
    status: str
    details: str | None = None


class StreamStatus(BaseModel):
    running: bool
    published_events: int
    last_event_id: str | None = None
