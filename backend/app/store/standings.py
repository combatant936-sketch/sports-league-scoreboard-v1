from app.models.schemas import Match, MatchStatus, StandingRow, Team


def calculate_standings(teams: list[Team], matches: list[Match]) -> list[StandingRow]:
    finished = [m for m in matches if m.status == MatchStatus.FINISHED]
    stats: dict[str, dict] = {}

    for team in teams:
        stats[team.id] = {
            "team_id": team.id,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "points": 0,
        }

    for match in finished:
        home = stats.get(match.home_team_id)
        away = stats.get(match.away_team_id)
        if home is None or away is None:
            continue

        home["played"] += 1
        away["played"] += 1
        home["goals_for"] += match.home_score
        home["goals_against"] += match.away_score
        away["goals_for"] += match.away_score
        away["goals_against"] += match.home_score

        if match.home_score > match.away_score:
            home["wins"] += 1
            home["points"] += 3
            away["losses"] += 1
        elif match.home_score < match.away_score:
            away["wins"] += 1
            away["points"] += 3
            home["losses"] += 1
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    team_names = {t.id: t.name for t in teams}
    rows = []
    for row in stats.values():
        gd = row["goals_for"] - row["goals_against"]
        rows.append(
            StandingRow(
                position=0,
                team_id=row["team_id"],
                team_name=team_names.get(row["team_id"], "Unknown"),
                played=row["played"],
                wins=row["wins"],
                draws=row["draws"],
                losses=row["losses"],
                goals_for=row["goals_for"],
                goals_against=row["goals_against"],
                goal_difference=gd,
                points=row["points"],
            )
        )

    rows.sort(key=lambda r: (-r.points, -r.goal_difference, -r.goals_for))
    return [
        row.model_copy(update={"position": index + 1}) for index, row in enumerate(rows)
    ]
