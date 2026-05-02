import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    os.environ.setdefault("LOG_DIRECTORY", "logs/")
    # Force in-memory limiter (slowapi falls back when REDIS_URL is unset).
    os.environ.pop("REDIS_URL", None)
    from app.main import app  # imported lazily so env is set first

    with TestClient(app) as c:
        yield c
