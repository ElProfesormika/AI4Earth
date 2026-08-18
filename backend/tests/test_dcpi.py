import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_dcpi_weights_sum_to_one():
    from app.services.dcpi_service import WEIGHTS

    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
