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
