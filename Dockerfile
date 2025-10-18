# ---- deps ----
FROM python:3.11-slim AS deps
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

# ---- runtime ----
FROM python:3.11-slim
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=deps /opt/venv /opt/venv
# kopiera in API-kod + modeller (pkl-filerna måste finnas i repo)
COPY app /app/app
COPY models /app/models
EXPOSE 8080
# starta FastAPI med uvicorn (ändra om du använder annat kommando)
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
