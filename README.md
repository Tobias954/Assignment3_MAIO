
# Virtual Diabetes Clinic — Complete Bundle

## Train locally (VS Code terminal)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
VERSION=v0.1 python src/train.py
VERSION=v0.2 python src/train.py
uvicorn src.serve:app --host 0.0.0.0 --port 8080
```

## Docker (build & run)
```bash
# Build images
docker build --build-arg VERSION=v0.1 -t diabetes-risk:v0.1 .
docker build --build-arg VERSION=v0.2 -t diabetes-risk:v0.2 .

# Run
docker run --rm -p 8081:8080 -e MODEL_VERSION=v0.1 diabetes-risk:v0.1
docker run --rm -p 8080:8080 -e MODEL_VERSION=v0.2 diabetes-risk:v0.2
```

## Endpoints
- GET `/health` → `{ "status":"ok", "model_version":"...", "metrics": {...} }`
- POST `/predict` (v0.1 & v0.2) → `{ "prediction": <float>, "model_version":"..." }`
- POST `/predict?include_flag=true` (v0.2 only) → adds `risk_flag`, `risk_score`, `threshold`

### Sample payload
```json
{ "age": 0.02, "sex": -0.044, "bmi": 0.06, "bp": -0.03, "s1": -0.02, "s2": 0.03, "s3": -0.02, "s4": 0.02, "s5": 0.02, "s6": -0.001 }
```

## Compose (MLflow + Jupyter + APIs)
```bash
docker compose up -d mlflow notebook
# MLflow:   http://localhost:5001
# Jupyter:  http://localhost:8888 (token: mlops)

docker compose up -d api_v01 api_v02
# v0.1: http://localhost:8081
# v0.2: http://localhost:8080
```
