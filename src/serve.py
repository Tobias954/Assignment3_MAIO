import os
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import joblib
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel

APP_ROOT = Path(__file__).resolve().parents[1]
MODELS_ROOT = APP_ROOT / "models"

# Default version comes from env, but we do not hardcode names.
DEFAULT_VERSION = os.getenv("MODEL_VERSION", "").strip() or None

app = FastAPI(title="FastAPI", version="0.1.0")

# -------- Discover & lazy-load --------
def discover_versions() -> Dict[str, Path]:
    """Find all versions as subfolders under models/, e.g. models/v0.1/."""
    versions = {}
    if MODELS_ROOT.exists():
        for p in MODELS_ROOT.iterdir():
            if p.is_dir():
                versions[p.name] = p
    return versions

AVAILABLE: Dict[str, Path] = discover_versions()

# Cache of loaded artefacts per version: {version: (model, scaler, meta)}
_CACHE: Dict[str, Tuple[object, Optional[object], dict]] = {}

def load_version(version: str) -> Tuple[object, Optional[object], dict]:
    """Load artefacts for a given version (cached)."""
    if version in _CACHE:
        return _CACHE[version]

    if version not in AVAILABLE:
        raise HTTPException(status_code=404, detail={
            "error": "version_not_found",
            "message": f"Requested version '{version}' not found.",
            "available_versions": sorted(AVAILABLE.keys()),
        })

    vdir = AVAILABLE[version]
    model_path = vdir / "model.joblib"
    scaler_path = vdir / "scaler.joblib"
    meta_path = vdir / "meta.json"  # if not present, we'll fallback
    metrics_path = vdir / "metrics.json"

    if not model_path.exists():
        # Endpoint exists, but model not baked or trained
        raise HTTPException(status_code=503, detail={
            "error": "model_missing",
            "message": f"Model artefact not found for version '{version}'. "
                       f"Expected at {str(model_path)}.",
        })

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path) if scaler_path.exists() else None

    meta: dict = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
    elif metrics_path.exists():
        # Some repos store metadata/threshold in metrics.json
        try:
            meta = json.loads(metrics_path.read_text(encoding="utf-8"))
        except Exception:
            meta = {}

    _CACHE[version] = (model, scaler, meta)
    return _CACHE[version]

def resolve_version(request_version: Optional[str], header_version: Optional[str]) -> str:
    """Pick version from query/header/env in a safe order, no hardcoding."""
    # 1) explicit query ?version=
    if request_version:
        return request_version
    # 2) header
    if header_version:
        return header_version
    # 3) default from env or single available
    if DEFAULT_VERSION:
        return DEFAULT_VERSION
    if len(AVAILABLE) == 1:
        return next(iter(AVAILABLE.keys()))
    # If none: ask client to specify
    raise HTTPException(status_code=400, detail={
        "error": "version_unspecified",
        "message": "No default model version is set and multiple versions are available. "
                   "Specify ?version=<name> or header X-Model-Version.",
        "available_versions": sorted(AVAILABLE.keys()),
    })

# -------- Schemas --------
class Features(BaseModel):
    age: float; sex: float; bmi: float; bp: float
    s1: float; s2: float; s3: float; s4: float; s5: float; s6: float

# -------- Endpoints --------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "default_version": DEFAULT_VERSION,
        "available_versions": sorted(AVAILABLE.keys()),
    }

@app.get("/")
def root():
    return {"status": "ok", "message": "Diabetes risk API"}

@app.post("/predict")
def predict(
    x: Features,
    include_flag: bool = Query(default=False, description="Include risk flag/score when metadata provides threshold"),
    version: Optional[str] = Query(default=None, description="Model version to use (e.g. v0.1, v0.2)"),
    x_model_version: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Model-Version"),
):
    # Determine version (query > header > env/default logic)
    v = resolve_version(version, x_model_version)

    # Load model/scaler/meta for that version
    model, scaler, meta = load_version(v)

    # Build input row
    X = [[x.age, x.sex, x.bmi, x.bp, x.s1, x.s2, x.s3, x.s4, x.s5, x.s6]]
    if scaler is not None:
        X = scaler.transform(X)
    y = float(model.predict(X)[0])

    resp = {"prediction": y, "model_version": v}

    if include_flag:
        # Use threshold if provided, otherwise omit risk fields gracefully
        threshold = meta.get("threshold")
        if threshold is not None:
            resp.update({
                "risk_flag": y >= float(threshold),
                "risk_score": y,
                "threshold": float(threshold),
            })
        else:
            # If no threshold, still valid response; we simply don't include flag fields.
            pass

    return resp
