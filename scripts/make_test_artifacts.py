import json, time, joblib
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np
from pathlib import Path

Xy = load_diabetes(as_frame=True)
X = Xy.frame.drop(columns=["target"])
y = Xy.frame["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipe = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
pipe.fit(X_train, y_train)

pred = pipe.predict(X_test)
rmse = float(np.sqrt(mean_squared_error(y_test, pred)))

outdir = Path("models") / "v0.2"
outdir.mkdir(parents=True, exist_ok=True)

joblib.dump(pipe, outdir / "model.joblib")

(outdir / "metrics.json").write_text(json.dumps({"rmse": rmse}, indent=2))
(outdir / "meta.json").write_text(json.dumps({
    "model_version": "v0.2",
    "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "algorithm": "StandardScaler+LinearRegression"
}, indent=2))

print("Saved:", outdir.resolve())
