import os

from fastapi.testclient import TestClient

from src.serve import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_base():
    payload = {
        "age": 0.02,
        "sex": -0.044,
        "bmi": 0.06,
        "bp": -0.03,
        "s1": -0.02,
        "s2": 0.03,
        "s3": -0.02,
        "s4": 0.02,
        "s5": 0.02,
        "s6": -0.001,
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    assert "prediction" in r.json()
