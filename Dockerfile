FROM python:3.11-slim AS deps
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=deps /opt/venv /opt/venv
COPY src /app/app
COPY models /app/models
EXPOSE 8080
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port 8080 --app-dir /app/src || uvicorn main:app --host 0.0.0.0 --port 8080 --app-dir /app/src"]
# Copy application source
COPY src /app/src
COPY models /app/models

# Ensure Python sees /app/src
ENV PYTHONPATH=/app/src
