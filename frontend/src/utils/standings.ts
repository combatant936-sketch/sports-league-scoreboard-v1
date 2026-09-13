import type { Match, StandingRow, Team } from '../types';

export function calculateStandings(teams: Team[], matches: Match[]): StandingRow[] {
  const finished = matches.filter((m) => m.status === 'finished');
  const stats = new Map<
    string,
    Omit<StandingRow, 'position' | 'teamName'>
  >();

  for (const team of teams) {
    stats.set(team.id, {
      teamId: team.id,
      played: 0,
      wins: 0,
      draws: 0,
      losses: 0,
      goalsFor: 0,
      goalsAgainst: 0,
      goalDifference: 0,
      points: 0,
    });
  }

  for (const match of finished) {
    const home = stats.get(match.homeTeamId);
    const away = stats.get(match.awayTeamId);
    if (!home || !away) continue;

    home.played += 1;
    away.played += 1;
    home.goalsFor += match.homeScore;
    home.goalsAgainst += match.awayScore;
    away.goalsFor += match.awayScore;
    away.goalsAgainst += match.homeScore;

    if (match.homeScore > match.awayScore) {
      home.wins += 1;
      home.points += 3;
      away.losses += 1;
    } else if (match.homeScore < match.awayScore) {
      away.wins += 1;
      away.points += 3;
      home.losses += 1;
    } else {
      home.draws += 1;
      away.draws += 1;
      home.points += 1;
      away.points += 1;
    }
  }

  const teamNames = new Map(teams.map((t) => [t.id, t.name]));

  return [...stats.values()]
    .map((row) => ({
      ...row,
      teamName: teamNames.get(row.teamId) ?? 'Unknown',
      goalDifference: row.goalsFor - row.goalsAgainst,
    }))
    .sort((a, b) => {
      if (b.points !== a.points) return b.points - a.points;
      if (b.goalDifference !== a.goalDifference) return b.goalDifference - a.goalDifference;
      return b.goalsFor - a.goalsFor;
    })
    .map((row, index) => ({ ...row, position: index + 1 }));
}
