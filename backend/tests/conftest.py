import os
from pathlib import Path

import pytest

# Arahkan ke SQLite sementara SEBELUM app diimpor, plus kredensial user awal.
_DB_PATH = Path(__file__).parent / "_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH.as_posix()}"
os.environ["INITIAL_USERNAME"] = "admin"
os.environ["INITIAL_PASSWORD"] = "admin123"
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import engine  # noqa: E402
from app.main import app  # noqa: E402


def _remove_db() -> None:
    engine.dispose()  # lepas koneksi agar file tidak terkunci (Windows)
    try:
        _DB_PATH.unlink(missing_ok=True)
    except PermissionError:
        pass


@pytest.fixture(scope="session", autouse=True)
def _cleanup_db():
    _remove_db()
    yield
    _remove_db()


@pytest.fixture()
def client():
    # `with` memicu lifespan: create_all + seed terhadap SQLite.
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_client(client):
    resp = client.post(
        "/auth/login", data={"username": "admin", "password": "admin123"}
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
