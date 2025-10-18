
# CHANGELOG

## v0.2
- Model: StandardScaler + RidgeCV (alphas=[0.1,1,10,100], 5-fold).
- Added optional risk flagging: POST /predict?include_flag=true returns {prediction, risk_flag, risk_score, threshold, model_version}.
- Threshold method: 80th percentile of train y (deterministic). meta.json stores threshold, seed, sigma.
- Metrics: rmse + precision/recall at threshold recorded in models/v0.2/metrics.json.

## v0.1
- Baseline: StandardScaler + LinearRegression.
- Endpoint: POST /predict returns continuous prediction only.
