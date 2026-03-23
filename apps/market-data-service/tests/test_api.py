from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_stream_control_flow() -> None:
    started = client.post('/streams/start')
    assert started.status_code == 200
    assert started.json()['running'] is True
    assert started.json()['published_events'] >= 1

    status = client.get('/streams/status')
    assert status.status_code == 200
    assert status.json()['running'] is True

    stopped = client.post('/streams/stop')
    assert stopped.status_code == 200
    assert stopped.json()['running'] is False


def test_preprocessing_endpoints() -> None:
    request = {'source': 'api', 'batch_size': 250}
    run_response = client.post('/preprocessing/run', json=request)
    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload['status'] == 'completed'

    replay_response = client.post('/preprocessing/replay', json=request)
    assert replay_response.status_code == 200
    replay_payload = replay_response.json()
    assert replay_payload['status'] == 'queued'

    status_response = client.get(f"/preprocessing/status/{payload['job_id']}")
    assert status_response.status_code == 200
    assert status_response.json()['status'] == 'completed'
