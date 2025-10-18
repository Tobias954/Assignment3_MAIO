FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installera beroenden i en venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Kopiera in kod och modeller (OBS: src får INTE ignoreras i .dockerignore)
COPY src/ /app/
COPY models/ /app/models/

EXPOSE 8080

# Starta API:t – förväntar src/app/main.py
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
