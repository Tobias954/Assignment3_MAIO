# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code and models (all versions)
COPY src ./src
COPY models ./models

# Default can be overridden at runtime: -e MODEL_VERSION=v0.2
ENV MODEL_VERSION=""

EXPOSE 8080
CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8080"]
