from fastapi.testclient import TestClient

ADMIN_EMAIL = "admin@league.com"
ADMIN_PASSWORD = "admin123"


def test_login_success(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == ADMIN_EMAIL
    assert "token" in data


def test_login_invalid_password(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["message"] == "Invalid email or password"


def test_me_without_token(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json() is None


def test_me_with_token(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == ADMIN_EMAIL


def test_logout(client: TestClient, auth_headers: dict[str, str]):
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 204
    me = client.get("/auth/me", headers=auth_headers)
    assert me.json() is None


def test_protected_route_requires_auth(client: TestClient):
    response = client.post("/teams", json={"name": "New Team", "logo": "🏟️"})
    assert response.status_code == 401
