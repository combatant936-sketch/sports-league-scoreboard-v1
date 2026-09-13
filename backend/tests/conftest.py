import pytest
from fastapi.testclient import TestClient

from app.auth.tokens import clear_tokens
from app.main import app
from app.store import reset_store

ADMIN_EMAIL = "admin@league.com"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(autouse=True)
def fresh_store():
    reset_store()
    clear_tokens()
    yield
    clear_tokens()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
