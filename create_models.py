import joblib
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error

Xy = load_diabetes(as_frame=True)
X = Xy.frame.drop(columns=["target"])
y = Xy.frame["target"]

RSEED = 42
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RSEED)

def train_and_save(model, outpath):
    pipe = Pipeline(steps=[("scaler", StandardScaler()), ("model", model)])
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)
    joblib.dump({"pipeline": pipe, "rmse": rmse}, outpath)
    print(f"✅ Saved {outpath}, RMSE={rmse:.3f}")

train_and_save(LinearRegression(), "models/model_v0.1.pkl")
train_and_save(Ridge(alpha=1.0, random_state=RSEED), "models/model_v0.2.pkl")
