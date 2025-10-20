# Assignment 3 – MAIO Project  
*(Virtual Diabetes Clinic Triage)*  

## 1. Project Overview  
This project develops a small machine learning service for a **virtual diabetes clinic**.  
Each week, nurses review patient check-ins (vitals, labs, lifestyle notes) to decide who needs a follow-up. The goal of this service is to predict a **short-term disease progression risk score**, allowing the clinic to prioritize follow-up calls efficiently.

The entire workflow — training, packaging, testing, and release — is automated via **GitHub Actions** and **Docker**.  
The system fulfills requirements for **portability, reproducibility, and observability**.

---

## 2. Data  
The project uses the open **scikit-learn Diabetes dataset** (`load_diabetes`) as a safe stand-in for de-identified EHR data.

```python
from sklearn.datasets import load_diabetes
Xy = load_diabetes(as_frame=True)
X = Xy.frame.drop(columns=["target"])
y = Xy.frame["target"]
```

`y` acts as a progression index — higher values ≈ greater deterioration risk.  
In production, this would correspond to rising HbA1c or complication risk.

---

## 3. Training and Reproducibility  
- Environment reproducibility via `requirements.txt` and Docker.  
- Deterministic training through fixed random seeds.  
- All models and metrics are stored in `models/<version>/` and `runs/<version>/`.  
- Clear instructions for both PowerShell and Docker execution.

---

## 4. Model Iterations  

| Version  | Model | Improvements |
|----------|--------|---------------|
| v0.1     | StandardScaler + LinearRegression | Baseline |
| v0.2     | Ridge Regression + improved preprocessing | Lower RMSE and smaller model |

All changes and reasoning are documented in `CHANGELOG.md`.

---

## 5. Metrics and Evaluation  

| Version | Date | RMSE | Training Time | Model Size | Notes |
|---------|------|------|----------------|-------------|--------|
| v0.1    | 2025-10-10 | 53.8 | 14.1 s | 4.8 MB | Baseline |
| v0.2    | 2025-10-18 | **47.2** | **12.4 s** | **3.9 MB** | Ridge Regression + optimized preprocessing |

RMSE is used as the main regression metric.  
If a binary “high-risk” flag is implemented, precision and recall could also be reported.

---

## 6. Docker Setup  
- Model is embedded directly into the Docker image.  
- Port **8080** (v0.2) and **8081** (v0.1).  
- Multi-stage build for smaller image size.  
- Health endpoint: `GET /health` returns model version and status as JSON.  
- Environment variable `MODEL_VERSION` controls which model is served.  
- Optional query parameter `include_flag` for detailed predictions.  
- Invalid input returns:  
  ```json
  {"error": "<description>"}
  ```  
  with HTTP 400 status.

---

## 7. CI/CD Pipeline (GitHub Actions)  
The repository includes two main workflows under `.github/workflows/`:

1. **`ci.yml`** – runs on each push/PR:  
   - Linting (flake8 / black)  
   - Unit tests and quick training smoke test  
   - Uploads model and metrics artifacts  

2. **`release.yml`** – runs on version tags (`v*`):  
   - Trains model (if needed)  
   - Builds Docker image  
   - Runs container smoke tests  
   - Pushes image to **GitHub Container Registry (GHCR)**  
   - Publishes **GitHub Release** with metrics and changelog  

Pulling the image manually:  
```bash
docker pull ghcr.io/tobias954/assignment3_maio:v0.2
docker run -p 8080:8080 ghcr.io/tobias954/assignment3_maio:v0.2
```

---

## 8. Run Locally (PowerShell)

### 1. Clone the repository
```powershell
git clone https://github.com/Tobias954/Assignment3_MAIO.git
cd Assignment3_MAIO
```

### 2. Set up Python environment
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Train the model
```powershell
python src/train.py --version v0.2 --seed 42
```
This saves the model in `models/v0.2/` and metrics in `runs/v0.2/`.

### 4. Run the service (v0.2)
```powershell
$env:MODEL_VERSION = "v0.2"
uvicorn src.serve:app --host 0.0.0.0 --port 8080 --reload
```

To serve v0.1:
```powershell
$env:MODEL_VERSION = "v0.1"
uvicorn src.serve:app --host 0.0.0.0 --port 8081 --reload
```

---

## 9. API Endpoints  

### `/health`
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET
```
Example response:  
```json
{"status": "ok", "model_version": "v0.2"}
```

### `/predict`
```powershell
$body = @{
    age = 0.02
    sex = -0.044
    bmi = 0.06
    bp  = -0.03
    s1  = -0.02
    s2  = 0.03
    s3  = -0.02
    s4  = 0.02
    s5  = 0.02
    s6  = -0.001
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/predict?include_flag=true" -Method POST -Body $body -ContentType "application/json"
```

Example response:  
```json
{
  "prediction": 123.45,
  "model_version": "v0.2",
  "details_included": true
}
```

---

## 10. Run with Docker

### Build image
```powershell
docker build -t maio-assignment3 .
```

### Run v0.2
```powershell
docker run -p 8080:8080 -e MODEL_VERSION=v0.2 maio-assignment3
```

### Run v0.1
```powershell
docker run -p 8081:8080 -e MODEL_VERSION=v0.1 maio-assignment3
```

### Health check in container
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET
```

---

## 11. Version History  

| Version | Date       | RMSE     | Training Time | Model Size | Notes |
|---------|------------|----------|---------------|------------|--------|
| v0.1    | 2025-10-10 | 53.8     | 14.1 s        | 4.8 MB     | Baseline |
| v0.2    | 2025-10-18 | **47.2** | **12.4 s**    | **3.9 MB** | Ridge Regression + preprocessing improvements |

See `CHANGELOG.md` for more details.

---

## 12. Authors  
- Tobias Hansson
- Monir Hasani
- Helin Youssef
- Anna Olofsson

---

## 13. Repository & Release Info  
GitHub: [https://github.com/Tobias954/Assignment3_MAIO](https://github.com/Tobias954/Assignment3_MAIO)  
Images published to GHCR:  
- `ghcr.io/tobias954/assignment3_maio:v0.1`  
- `ghcr.io/tobias954/assignment3_maio:v0.2`  
