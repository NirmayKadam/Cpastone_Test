from fastapi import APIRouter, Depends

from libs.event_schemas import JobStatus, PreprocessingJobRequest, StreamStatus

from app.dependencies import get_market_data_service
from app.services import MarketDataService

router = APIRouter()


@router.get('/health')
async def health(service: MarketDataService = Depends(get_market_data_service)) -> dict[str, str]:
    return await service.health()


@router.get('/health/ready')
async def ready(service: MarketDataService = Depends(get_market_data_service)) -> dict[str, str]:
    return await service.ready()


@router.get('/health/live')
async def live(service: MarketDataService = Depends(get_market_data_service)) -> dict[str, str]:
    return await service.live()


@router.post('/streams/start', response_model=StreamStatus)
async def start_stream(service: MarketDataService = Depends(get_market_data_service)) -> StreamStatus:
    return await service.start_stream()


@router.post('/streams/stop', response_model=StreamStatus)
async def stop_stream(service: MarketDataService = Depends(get_market_data_service)) -> StreamStatus:
    return await service.stop_stream()


@router.get('/streams/status', response_model=StreamStatus)
async def stream_status(service: MarketDataService = Depends(get_market_data_service)) -> StreamStatus:
    return await service.stream_status()


@router.post('/preprocessing/run', response_model=JobStatus)
async def run_preprocessing(
    request: PreprocessingJobRequest,
    service: MarketDataService = Depends(get_market_data_service),
) -> JobStatus:
    return await service.run_preprocessing(request)


@router.post('/preprocessing/replay', response_model=JobStatus)
async def replay_preprocessing(
    request: PreprocessingJobRequest,
    service: MarketDataService = Depends(get_market_data_service),
) -> JobStatus:
    return await service.replay_preprocessing(request)


@router.get('/preprocessing/status/{job_id}', response_model=JobStatus)
async def preprocessing_status(
    job_id: str,
    service: MarketDataService = Depends(get_market_data_service),
) -> JobStatus:
    return await service.preprocessing_status(job_id)
