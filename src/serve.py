# src/serve.py
import json
import math
import os
from pathlib import Path
from typing import Tuple, Dict, Any

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ------------------------------------------------------------
# Artefakt-platser (MODEL_VERSION sätts via env, t.ex. v0.2)
# ------------------------------------------------------------
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


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_artifacts() -> Tuple[Any, Dict[str, Any], Dict[str, Any]]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)

    metrics: Dict[str, Any] = {}
    if METRICS_PATH.exists():
        metrics = _load_json(METRICS_PATH)

    if not META_PATH.exists():
        # Saknas meta => vi kan inte härleda threshold
        raise FileNotFoundError(
            f"Meta file not found at {META_PATH}. It must include a numeric 'threshold'."
        )
    meta = _load_json(META_PATH)

    # Validera att threshold finns och är numerisk
    if "threshold" not in meta:
        raise KeyError(
            f"'threshold' key missing in {META_PATH}. Add e.g. {{\"threshold\": 235}}"
        )
    try:
        # Säkerställ float (om str i filen)
        meta["threshold"] = float(meta["threshold"])
    except Exception as e:
        raise ValueError(
            f"'threshold' in {META_PATH} must be numeric. Got: {meta.get('threshold')}"
        ) from e

    return model, metrics, meta


def _sigmoid(x: float) -> float:
    # Behövs om ni i framtiden vill använda mjuk score/klassificering
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


app = FastAPI(title="Virtual Diabetes Clinic — Progression Risk Service")

# Ladda artefakter vid uppstart
MODEL, METRICS, META = load_artifacts()


@app.get("/health")
def health():
    # Exponera threshold från meta för transparens
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "metrics": METRICS,
        "threshold": META.get("threshold"),
    }


@app.post("/predict")
def predict(feats: PatientFeatures):
    """
    Returnerar:
      {
        "prediction": <float>,
        "model_version": "<ver>",
        "high_risk": <bool>   # True/False baserat på meta['threshold']
      }
    """
    try:
        X = [[getattr(feats, f) for f in FEATURES]]
        pred = float(MODEL.predict(X)[0])

        thr = META["threshold"]  # garanterat numerisk från load_artifacts()
        high = bool(pred >= thr)

        return {
            "prediction": pred,
            "model_version": MODEL_VERSION,
            "high_risk": high,
        }
    except Exception as e:
        # Klientvänligt felmeddelande
        raise HTTPException(
            status_code=500,
            detail={
                "error": "prediction_failed",
                "message": str(e),
            },
        )
