import json
import math
import os
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

MODEL_DIR = Path(os.getenv("MODEL_DIR", "models"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "v0.2")
MODEL_PATH = MODEL_DIR / MODEL_VERSION / "model.joblib"
METRICS_PATH = MODEL_DIR / MODEL_VERSION / "metrics.json"
META_PATH = MODEL_DIR / MODEL_VERSION / "meta.json"

FEATURES = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]


class PatientFeatures(BaseModel):
    age: float = Field(..., description="Normalized age")
    sex: float
    bmi: float
    bp: float
    s1: float
    s2: float
    s3: float
    s4: float
    s5: float
    s6: float


def load_artifacts():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    metrics = {}
    if METRICS_PATH.exists():
        with open(METRICS_PATH) as f:
            metrics = json.load(f)
    meta = {}
    if META_PATH.exists():
        with open(META_PATH) as f:
            meta = json.load(f)
    return model, metrics, meta


app = FastAPI(title="Virtual Diabetes Clinic — Progression Risk Service")

MODEL, METRICS, META = load_artifacts()


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION, "metrics": METRICS}


def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


@app.post("/predict")
def predict(
    feats: PatientFeatures,
    include_flag: bool = Query(
        False, description="(v0.2) include risk_flag & risk_score"
    ),
):
    try:
        X = [[getattr(feats, f) for f in FEATURES]]
        pred = float(MODEL.predict(X)[0])
        resp = {"prediction": pred, "model_version": MODEL_VERSION}
        # Optional flagging only for v0.2 with meta present
        if include_flag and MODEL_VERSION == "v0.2" and META:
            thr = float(META.get("threshold"))
            sigma = float(META.get("sigma", 1.0))
            score = _sigmoid((pred - thr) / sigma)
            resp.update(
                {
                    "risk_flag": bool(pred >= thr),
                    "risk_score": round(score, 4),
                    "threshold": thr,
                }
            )
        return resp
    except Exception as e:
        raise HTTPException(
            status_code=400, detail={"error": "bad_request", "message": str(e)}
        )
