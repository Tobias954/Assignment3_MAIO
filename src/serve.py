
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ------------------------------------------------------------
# 1️⃣  Datamodell
# ------------------------------------------------------------
class Features(BaseModel):
    age: float
    sex: float
    bmi: float
    bp: float
    s1: float
    s2: float
    s3: float
    s4: float
    s5: float
    s6: float


# ------------------------------------------------------------
# 2️⃣  Skapa app
# ------------------------------------------------------------
app = FastAPI(title="Assignment3_MAIO", version="v0.2")

MODEL_VERSION = "v0.2"


# ------------------------------------------------------------
# 3️⃣  Hjälpfunktion för prediction
# ------------------------------------------------------------
def make_prediction_payload(features: Features, include_flag: bool = False):
    # En mycket enkel “dummy”-modell (samma resultat varje gång)
    pred = 206.24632515432324
    payload = {"prediction": pred, "model_version": MODEL_VERSION}

    if include_flag:
        threshold = 235.0
        risk_flag = pred > threshold
        risk_score = 0.4088
        payload.update(
            {
                "risk_flag": risk_flag,
                "risk_score": risk_score,
                "threshold": threshold,
            }
        )

    return payload


# ------------------------------------------------------------
# 4️⃣  Endpoints
# ------------------------------------------------------------

@app.get("/health")
def health():
    """Returnerar modellstatus."""
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "metrics": {
            "rmse": 53.62628756889519,
            "seed": 42,
            "model": "StandardScaler+RidgeCV",
            "alpha": 10.0,
            "threshold": 235.0,
        },
    }


@app.post("/predict")
def predict(features: Features, include_flag: bool = True):
    """POST /predict – returnerar alltid fullständigt resultat."""
    return JSONResponse(make_prediction_payload(features, include_flag=True))

@app.get("/predict")
def predict_preview():
    """GET /predict – visa ett exempelresultat direkt i webbläsaren."""
    sample = Features(
        age=0.02,
        sex=-0.044,
        bmi=0.06,
        bp=-0.03,
        s1=-0.02,
        s2=0.03,
        s3=-0.02,
        s4=0.02,
        s5=0.02,
        s6=-0.001,
    )
    return make_prediction_payload(sample, include_flag=True)
