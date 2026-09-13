from fastapi.testclient import TestClient


def test_get_league(client: TestClient):
    response = client.get("/league")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Premier City League"
    assert data["season"] == "2025/26"
    assert data["status"] == "active"


def test_update_league(client: TestClient, auth_headers: dict[str, str]):
    response = client.patch(
        "/league",
        headers=auth_headers,
        json={"name": "Updated League"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated League"
