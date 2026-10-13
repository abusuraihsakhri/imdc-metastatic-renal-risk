from fastapi.testclient import TestClient
from agents.api import app
from imdc_risk import FIELDS


def test_imdc_api():
    client = TestClient(app)
    factors = {name: False for name in FIELDS}
    response = client.post("/api/imdc", json=factors)
    assert response.status_code == 200
    assert response.json()["score"] == 0
    assert response.json()["classification"] == "Favorable"
    factors[FIELDS[0]] = True
    factors[FIELDS[1]] = True
    factors[FIELDS[2]] = True
    assert client.post("/api/imdc", json=factors).json()["classification"] == "Poor"
    assert client.post("/api/imdc", json={"v1": 12}).status_code == 422
    assert client.post("/api/imdc", json={**factors, "unknown": 1}).status_code == 422
    assert client.post("/api/imdc", json={**factors, FIELDS[0]: "yes"}).status_code == 422
