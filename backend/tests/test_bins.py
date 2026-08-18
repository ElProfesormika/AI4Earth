import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


import pytest

@pytest.mark.skip(reason="requires PostgreSQL")
def test_list_bins_empty_or_populated(client):
    resp = client.get("/api/v1/bins")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
