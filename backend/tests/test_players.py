from fastapi.testclient import TestClient


def test_list_players(client: TestClient):
    response = client.get("/players")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_list_players_by_team(client: TestClient):
    response = client.get("/players", params={"teamId": "team-1"})
    assert response.status_code == 200
    players = response.json()
    assert len(players) == 3
    assert all(p["teamId"] == "team-1" for p in players)


def test_create_player(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/players",
        headers=auth_headers,
        json={
            "name": "New Star",
            "jerseyNumber": 99,
            "position": "FWD",
            "isCaptain": False,
            "teamId": "team-1",
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Star"


def test_captain_demotion(client: TestClient, auth_headers: dict[str, str]):
    client.post(
        "/players",
        headers=auth_headers,
        json={
            "name": "Captain Two",
            "jerseyNumber": 88,
            "position": "MID",
            "isCaptain": True,
            "teamId": "team-1",
        },
    )
    players = client.get("/players", params={"teamId": "team-1"}).json()
    captains = [p for p in players if p["isCaptain"]]
    assert len(captains) == 1
    assert captains[0]["name"] == "Captain Two"
