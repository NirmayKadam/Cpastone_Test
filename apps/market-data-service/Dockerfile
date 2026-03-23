FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
COPY apps/market-data-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/market-data-service/app ./app
COPY libs ./libs
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
