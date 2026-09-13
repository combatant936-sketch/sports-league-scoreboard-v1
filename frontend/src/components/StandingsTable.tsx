import type { StandingRow } from '../types';

export function StandingsTable({ standings }: { standings: StandingRow[] }) {
  if (standings.length === 0) {
    return <p className="empty-state">No standings data yet.</p>;
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Team</th>
            <th>P</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>GF</th>
            <th>GA</th>
            <th>GD</th>
            <th>Pts</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((row) => (
            <tr key={row.teamId}>
              <td>{row.position}</td>
              <td className="team-cell">{row.teamName}</td>
              <td>{row.played}</td>
              <td>{row.wins}</td>
              <td>{row.draws}</td>
              <td>{row.losses}</td>
              <td>{row.goalsFor}</td>
              <td>{row.goalsAgainst}</td>
              <td className={row.goalDifference > 0 ? 'positive' : row.goalDifference < 0 ? 'negative' : ''}>
                {row.goalDifference > 0 ? `+${row.goalDifference}` : row.goalDifference}
              </td>
              <td className="points-cell">{row.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
