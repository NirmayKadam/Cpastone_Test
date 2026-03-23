from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import ValidationError

from libs.event_schemas import JobStatus, PreprocessingJobRequest, StreamStatus

from app.adapters.mock_nse import MockNSEAdapter
from app.core.config import Settings, settings
from app.pipelines.normalizer import normalize_tick
from app.streams.backbone import InMemoryEventBackbone


class MarketDataService:
    def __init__(
        self,
        config: Settings = settings,
        adapter: MockNSEAdapter | None = None,
        backbone: InMemoryEventBackbone | None = None,
    ) -> None:
        self.config = config
        self.adapter = adapter or MockNSEAdapter()
        self.backbone = backbone or InMemoryEventBackbone()
        self.running = False
        self.published_events = 0
        self.last_event_id: str | None = None
        self.jobs: dict[str, JobStatus] = {}

    async def health(self) -> dict[str, str]:
        return {'status': 'ok'}

    async def ready(self) -> dict[str, str]:
        return {'status': 'ready'}

    async def live(self) -> dict[str, str]:
        return {'status': 'live'}

    async def start_stream(self) -> StreamStatus:
        if not self.running:
            self.running = True
            await self._publish_control('start')
            await self.poll_once()
        return await self.stream_status()

    async def stop_stream(self) -> StreamStatus:
        if self.running:
            self.running = False
            await self._publish_control('stop')
        return await self.stream_status()

    async def stream_status(self) -> StreamStatus:
        return StreamStatus(
            running=self.running,
            published_events=self.published_events,
            last_event_id=self.last_event_id,
        )

    async def poll_once(self) -> str | None:
        try:
            normalized = normalize_tick(await self.adapter.get_next_tick())
        except (ValidationError, ValueError) as exc:
            await self.backbone.publish(
                self.config.data_stream_dlq_topic,
                {'error': str(exc), 'timestamp': datetime.now(timezone.utc).isoformat()},
            )
            return None

        self.last_event_id = await self.backbone.publish(
            self.config.data_stream_tick_topic,
            normalized.stream_payload(),
        )
        self.published_events += 1
        return self.last_event_id

    async def run_preprocessing(self, request: PreprocessingJobRequest) -> JobStatus:
        job_id = str(uuid4())
        status = JobStatus(job_id=job_id, status='completed', details=f'batch_size={request.batch_size}')
        self.jobs[job_id] = status
        await self.backbone.publish(
            self.config.preprocessing_request_topic,
            request.model_dump(mode='json'),
        )
        await self.backbone.publish(
            self.config.preprocessing_completed_topic,
            status.model_dump(mode='json'),
        )
        return status

    async def replay_preprocessing(self, request: PreprocessingJobRequest) -> JobStatus:
        job_id = str(uuid4())
        status = JobStatus(job_id=job_id, status='queued', details='replay_requested')
        self.jobs[job_id] = status
        await self.backbone.publish(
            self.config.preprocessing_request_topic,
            {
                **request.model_dump(mode='json'),
                'mode': 'replay',
            },
        )
        return status

    async def preprocessing_status(self, job_id: str) -> JobStatus:
        return self.jobs.get(job_id, JobStatus(job_id=job_id, status='not_found', details='unknown_job'))

    async def _publish_control(self, action: str) -> str:
        return await self.backbone.publish(
            self.config.data_stream_control_topic,
            {'action': action, 'timestamp': datetime.now(timezone.utc).isoformat()},
        )
