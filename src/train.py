import json
import os
from pathlib import Path

import joblib
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.metrics import mean_squared_error, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = int(os.getenv("SEED", "42"))
OUT_DIR = Path(os.getenv("OUT_DIR", "models"))
VERSION = os.getenv("VERSION", "v0.2")


def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def data():
    d = load_diabetes(as_frame=True)
    X = d.frame.drop(columns=["target"])
    y = d.frame["target"]
    return X, y


def train_v01():
    X, y = data()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=SEED)
    pipe = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
    pipe.fit(Xtr, ytr)
    r = rmse(yte, pipe.predict(Xte))
    metrics = {"rmse": r, "seed": SEED, "model": "StandardScaler+LinearRegression"}
    return pipe, metrics, {}


def train_v02():
    X, y = data()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=SEED)
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("ridge", RidgeCV(alphas=[0.1, 1, 10, 100], cv=5)),
        ]
    )
    pipe.fit(Xtr, ytr)
    preds = pipe.predict(Xte)
    r = rmse(yte, preds)

    # Deterministic threshold: 80th percentile of y_train
    threshold = float(np.percentile(ytr, 80))
    sigma = float(max(np.std(ytr), 1e-6))  # for smooth risk_score

    # Evaluate precision/recall at that threshold on test (for CHANGELOG)
    yte_pos = (yte >= threshold).astype(int)
    ypred_pos = (preds >= threshold).astype(int)
    prec = float(precision_score(yte_pos, ypred_pos, zero_division=0))
    rec = float(recall_score(yte_pos, ypred_pos, zero_division=0))

    metrics = {
        "rmse": r,
        "seed": SEED,
        "model": "StandardScaler+RidgeCV",
        "alpha": float(pipe.named_steps["ridge"].alpha_),
        "threshold_metrics": {
            "threshold_method": "p80_of_train_y",
            "threshold": threshold,
            "precision_at_threshold": prec,
            "recall_at_threshold": rec,
        },
    }
    meta = {
        "threshold": threshold,
        "method": "p80_of_train_y",
        "seed": SEED,
        "sigma": sigma,
    }
    return pipe, metrics, meta


if __name__ == "__main__":
    if VERSION == "v0.1":
        model, metrics, meta = train_v01()
    elif VERSION == "v0.2":
        model, metrics, meta = train_v02()
    else:
        raise ValueError("VERSION must be v0.1 or v0.2")
    out = OUT_DIR / VERSION
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out / "model.joblib")
    with open(out / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    if meta:
        with open(out / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)
    print(json.dumps({"version": VERSION, **metrics}, indent=2))
