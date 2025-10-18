
# Can be opened in Jupyter as a script. Logs a baseline run to MLflow.
import os, mlflow
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
mlflow.set_experiment("diabetes_baseline")

Xy = load_diabetes(as_frame=True)
X = Xy.frame.drop(columns=["target"])
y = Xy.frame["target"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run(run_name="baseline-lr"):
    pipe = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
    pipe.fit(Xtr, ytr)
    preds = pipe.predict(Xte)
    rmse = mean_squared_error(yte, preds, squared=False)
    mlflow.log_metric("rmse", rmse)
    mlflow.sklearn.log_model(pipe, "model", input_example=Xte.iloc[:1])
    print({"rmse": rmse})
