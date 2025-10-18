FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- deps ----
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- code & model ----
# VI KOPIERAR ALLT INNE I src/ TILL /app/
COPY src/ /app/
COPY models/ /app/models/

EXPOSE 8080

# ---- robust start ----
# Prova i ordning:
#  1) app/main.py   -> uvicorn app.main:app
#  2) main.py       -> uvicorn main:app
#  3) api.py        -> uvicorn api:app
#  4) server.py     -> uvicorn server:app
# Om inget finns: lista /app och avsluta med fel.
CMD ["sh","-c", "\
  if [ -f /app/app/main.py ]; then \
    uvicorn app.main:app --host 0.0.0.0 --port 8080; \
  elif [ -f /app/main.py ]; then \
    uvicorn main:app --host 0.0.0.0 --port 8080; \
  elif [ -f /app/api.py ]; then \
    uvicorn api:app --host 0.0.0.0 --port 8080; \
  elif [ -f /app/server.py ]; then \
    uvicorn server:app --host 0.0.0.0 --port 8080; \
  else \
    echo '❌ Hittar ingen ASGI-entré (app.main/main/api/server). Innehåll i /app:'; \
    ls -al /app; \
    exit 1; \
  fi"]
