from fastapi.testclient import TestClient


def test_list_teams(client: TestClient):
    response = client.get("/teams")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_get_team(client: TestClient):
    response = client.get("/teams/team-1")
    assert response.status_code == 200
    assert response.json()["name"] == "North United"


def test_create_team(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/teams",
        headers=auth_headers,
        json={"name": "Harbor FC", "logo": "⚓"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Harbor FC"


def test_update_team(client: TestClient, auth_headers: dict[str, str]):
    response = client.patch(
        "/teams/team-1",
        headers=auth_headers,
        json={"name": "North FC"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "North FC"


def test_delete_team_with_players_fails(client: TestClient, auth_headers: dict[str, str]):
    response = client.delete("/teams/team-1", headers=auth_headers)
    assert response.status_code == 400


def test_delete_unused_team(client: TestClient, auth_headers: dict[str, str]):
    create = client.post(
        "/teams",
        headers=auth_headers,
        json={"name": "Temp Team", "logo": "🧪"},
    )
    team_id = create.json()["id"]
    response = client.delete(f"/teams/{team_id}", headers=auth_headers)
    assert response.status_code == 204
