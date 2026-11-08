# Author: Nicola Antonello
"""The health check that Kubernetes probes."""


def test_healthz_reports_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
