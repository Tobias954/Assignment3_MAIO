
FROM python:3.11-slim

ARG VERSION=v0.2
ENV VERSION=${VERSION} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
# Train and bake model into the image (models/<VERSION>)
RUN python src/train.py

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health || exit 1
CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8080"]
