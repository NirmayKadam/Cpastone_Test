from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_readiness_and_liveness() -> None:
    assert client.get('/health/ready').json() == {'status': 'ready'}
    assert client.get('/health/live').json() == {'status': 'live'}
