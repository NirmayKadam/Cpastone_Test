from app.services import MarketDataService

service = MarketDataService()


def get_market_data_service() -> MarketDataService:
    return service
