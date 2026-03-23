from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Market Data Service'
    app_env: str = 'development'
    log_level: str = 'INFO'
    data_stream_tick_topic: str = 'market.ticks.normalized'
    data_stream_control_topic: str = 'market.control'
    data_stream_dlq_topic: str = 'market.ticks.dlq'
    preprocessing_request_topic: str = 'market.preprocessing.requests'
    preprocessing_completed_topic: str = 'market.preprocessing.completed'
    preprocess_batch_size: int = 500
    normalization_timezone: str = 'Asia/Kolkata'
    redis_url: str = Field(default='redis://redis:6379/0', alias='REDIS_URL')

    model_config = SettingsConfigDict(env_file='.env', extra='ignore', populate_by_name=True)


settings = Settings()
