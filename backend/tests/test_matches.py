from fastapi.testclient import TestClient


def test_list_matches(client: TestClient):
    response = client.get("/matches")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_filter_matches_by_status(client: TestClient):
    response = client.get("/matches", params={"status": "scheduled"})
    assert response.status_code == 200
    assert all(m["status"] == "scheduled" for m in response.json())


def test_create_match(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "homeTeamId": "team-1",
            "awayTeamId": "team-2",
            "scheduledAt": "2026-10-01T15:00:00.000Z",
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "scheduled"


def test_create_match_same_team_fails(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "homeTeamId": "team-1",
            "awayTeamId": "team-1",
            "scheduledAt": "2026-10-01T15:00:00.000Z",
        },
    )
    assert response.status_code == 400


def test_match_lifecycle(client: TestClient, auth_headers: dict[str, str]):
    create = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "homeTeamId": "team-1",
            "awayTeamId": "team-4",
            "scheduledAt": "2026-10-05T15:00:00.000Z",
        },
    )
    match_id = create.json()["id"]

    start = client.post(f"/matches/{match_id}/start", headers=auth_headers)
    assert start.status_code == 200
    assert start.json()["status"] == "live"

    event = client.post(
        f"/matches/{match_id}/events",
        headers=auth_headers,
        json={
            "teamId": "team-1",
            "playerId": "player-2",
            "eventType": "goal",
            "minute": 10,
            "description": "Test goal",
        },
    )
    assert event.status_code == 201

    match = client.get(f"/matches/{match_id}").json()
    assert match["homeScore"] == 1

    finish = client.post(f"/matches/{match_id}/finish", headers=auth_headers)
    assert finish.status_code == 200
    assert finish.json()["status"] == "finished"


def test_goal_removed_recalculates_score(client: TestClient, auth_headers: dict[str, str]):
    create = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "homeTeamId": "team-2",
            "awayTeamId": "team-3",
            "scheduledAt": "2026-10-06T15:00:00.000Z",
        },
    )
    match_id = create.json()["id"]
    client.post(f"/matches/{match_id}/start", headers=auth_headers)

    event = client.post(
        f"/matches/{match_id}/events",
        headers=auth_headers,
        json={
            "teamId": "team-2",
            "playerId": "player-5",
            "eventType": "goal",
            "minute": 5,
        },
    )
    event_id = event.json()["id"]
    assert client.get(f"/matches/{match_id}").json()["homeScore"] == 1

    delete = client.delete(f"/matches/{match_id}/events/{event_id}", headers=auth_headers)
    assert delete.status_code == 204
    assert client.get(f"/matches/{match_id}").json()["homeScore"] == 0


def test_cancel_match_clears_events(client: TestClient, auth_headers: dict[str, str]):
    create = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "homeTeamId": "team-1",
            "awayTeamId": "team-4",
            "scheduledAt": "2026-10-07T15:00:00.000Z",
        },
    )
    match_id = create.json()["id"]
    client.post(f"/matches/{match_id}/start", headers=auth_headers)
    client.post(
        f"/matches/{match_id}/events",
        headers=auth_headers,
        json={
            "teamId": "team-1",
            "playerId": "player-2",
            "eventType": "goal",
            "minute": 1,
        },
    )

    cancel = client.post(f"/matches/{match_id}/cancel", headers=auth_headers)
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"
    assert client.get(f"/matches/{match_id}/events").json() == []
