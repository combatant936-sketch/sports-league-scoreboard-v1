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


def test_update_player(client: TestClient, auth_headers: dict[str, str]):
    response = client.patch(
        "/players/player-1",
        headers=auth_headers,
        json={
            "name": "Alex Updated",
            "jerseyNumber": 12,
            "position": "MID",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alex Updated"
    assert data["jerseyNumber"] == 12
    assert data["position"] == "MID"


def test_delete_player_referenced_in_events_fails(
    client: TestClient, auth_headers: dict[str, str]
):
    # player-2 is in match-1 event-1
    response = client.delete("/players/player-2", headers=auth_headers)
    assert response.status_code == 400
    assert "events" in response.json()["detail"]["message"].lower()


def test_delete_player_success(client: TestClient, auth_headers: dict[str, str]):
    # Create player not in any events
    create_res = client.post(
        "/players",
        headers=auth_headers,
        json={
            "name": "Temporary Player",
            "jerseyNumber": 55,
            "position": "DEF",
            "isCaptain": False,
            "teamId": "team-1",
        },
    )
    player_id = create_res.json()["id"]

    del_res = client.delete(f"/players/{player_id}", headers=auth_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/players/{player_id}")
    assert get_res.status_code == 404
