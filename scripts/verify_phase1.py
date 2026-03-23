from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    '.env.example',
    'docker-compose.yml',
    'Makefile',
    'pyproject.toml',
    '.github/workflows/ci.yml',
    'configs/prometheus/prometheus.yml',
    'infra/k8s/base/namespace.yaml',
    'apps/api-gateway/app/main.py',
    'apps/market-data-service/app/main.py',
    'apps/quant-engine/app/main.py',
    'apps/ml-service/app/main.py',
    'apps/worker-orchestrator/app/main.py',
    'apps/frontend/package.json',
    'apps/market-data-service/app/services.py',
    'libs/event_schemas/market.py',
]

REQUIRED_PHRASES = {
    '.env.example': ['APP_ENV=development', 'REDIS_URL=', 'TIMESCALE_URL='],
    'docker-compose.yml': ['api-gateway:', 'market-data-service:', 'frontend:'],
    'apps/market-data-service/app/api/routes.py': [
        '/streams/start',
        '/preprocessing/run',
        '/health/ready',
    ],
}


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f'Missing required files: {missing}')

    for rel_path, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel_path).read_text()
        absent = [phrase for phrase in phrases if phrase not in text]
        if absent:
            raise SystemExit(f'Missing phrases in {rel_path}: {absent}')

    print('Phase scaffold verification passed.')


if __name__ == '__main__':
    main()
