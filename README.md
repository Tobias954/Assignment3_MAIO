# Diabetes Risk Prediction Service — Assignment 3 (MAIO)

A FastAPI-based MLOps project for predicting short-term disease progression in diabetes patients.
The system includes two models (v0.1 and v0.2) and can be run in parallel in Docker containers via the MODEL_VERSION environment variable.

Contents:

Description
Structure
Installation and running locally
Build Docker image
Run two versions in parallel
API endpoints
Example requests
Common issues
## Description

The project trains and serves models based on scikit-learn’s diabetes dataset (load_diabetes).
The goal is to provide a reproducible pipeline with versioned models:

Version	Model type	           Improvement	                Port
v0.1	LinearRegression	    Baseline	                8081
v0.2	Ridge / RandomForest	Improved RMSE & risk flag	8080

Each model version is saved under models/<version>/ and is dynamically loaded by the API.

🗂 
## 🗂 Structure

```
Assignment3_MAIO/
├── src/
│   ├── train.py
│   └── serve.py
├── models/
│   ├── v0.1/
│   └── v0.2/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Install and run locally

```powershell
git clone https://github.com/Tobias954/Assignment3_MAIO.git
cd Assignment3_MAIO
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:VERSION = "v0.1"
python .\src\train.py

$env:VERSION = "v0.2"
python .\src\train.py

$env:MODEL_VERSION = "v0.1"
uvicorn src.serve:app --host 0.0.0.0 --port 8081
```

## Building a Docker image

```powershell
docker build --no-cache -t diabetes-risk:multi .
```

## Run two versions in parallel

```powershell
docker run --name diabetes_v01 --rm -p 8081:8080 -e MODEL_VERSION=v0.1 diabetes-risk:multi
docker run --name diabetes_v02 --rm -p 8080:8080 -e MODEL_VERSION=v0.2 diabetes-risk:multi
```

##  API-endpoints

| Method | Endpoint | Beskrivning |
|---------|-----------|-------------|
| `GET` | `/health` | Status, aktiv modellversion, tillgängliga versioner |
| `POST` | `/predict` | Tar emot patientdata och returnerar prediktion |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/openapi.json` | OpenAPI-schema |

## 🧪 Exempelanrop

```powershell
$body = @{
  age = 0.02; sex = -0.044; bmi = 0.06; bp = -0.03;
  s1 = -0.02; s2 = 0.03; s3 = -0.02; s4 = 0.02; s5 = 0.02; s6 = -0.001
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8081/predict" -Method Post -ContentType "application/json" -Body $body
Invoke-RestMethod -Uri "http://localhost:8080/predict?include_flag=true" -Method Post -ContentType "application/json" -Body $body
```

## ⚙️ Docker Compose (valfritt)

```yaml
version: "3.9"
services:
  api_v01:
    build: .
    image: diabetes-risk:multi
    ports:
      - "8081:8080"
    environment:
      - MODEL_VERSION=v0.1

  api_v02:
    build: .
    image: diabetes-risk:multi
    ports:
      - "8080:8080"
    environment:
      - MODEL_VERSION=v0.2
```

Starts both:
```powershell
docker compose up -d --build
```

##  Vanliga problem

| Problem | Orsak | Lösning |
|----------|--------|----------|
| `404 Not Found` | Modell saknas i imagen | Kör `python src/train.py` innan build |
| `503 model_missing` | Modellfil ej kopierad | Kontrollera `.dockerignore` och Dockerfile |
| `Method Not Allowed` | `/predict` kräver `POST` | Använd Swagger (`/docs`) |
| Modellversion saknas | Fel `MODEL_VERSION` | Se `/health` |