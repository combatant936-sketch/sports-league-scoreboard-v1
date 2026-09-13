from fastapi.testclient import TestClient


def test_standings(client: TestClient):
    response = client.get("/standings")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 4
    assert rows[0]["position"] == 1
    assert "teamName" in rows[0]
    assert "points" in rows[0]

    north = next(r for r in rows if r["teamId"] == "team-1")
    assert north["played"] == 1
    assert north["wins"] == 1
    assert north["points"] == 3


def test_standings_draw_points(client: TestClient):
    response = client.get("/standings")
    assert response.status_code == 200
    rows = response.json()

    # match-2 was team-3 vs team-4, score 1-1 (draw)
    team3 = next(r for r in rows if r["teamId"] == "team-3")
    team4 = next(r for r in rows if r["teamId"] == "team-4")

    assert team3["played"] == 1
    assert team3["draws"] == 1
    assert team3["points"] == 1
    assert team3["goalDifference"] == 0

    assert team4["played"] == 1
    assert team4["draws"] == 1
    assert team4["points"] == 1
    assert team4["goalDifference"] == 0


def test_standings_order(client: TestClient):
    response = client.get("/standings")
    assert response.status_code == 200
    rows = response.json()

    # Verify positions are sequential 1 to 4
    positions = [r["position"] for r in rows]
    assert positions == [1, 2, 3, 4]

    # Verify descending points
    points = [r["points"] for r in rows]
    assert points == sorted(points, reverse=True)
