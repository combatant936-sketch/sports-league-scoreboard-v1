import { Link, useParams } from 'react-router-dom';
import * as api from '../api/client';
import { useAsyncData } from '../hooks/useAsyncData';

export function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const team = useAsyncData(() => api.getTeam(id!), [id]);
  const players = useAsyncData(() => api.getPlayers(id!), [id]);

  if (team.loading) return <div className="page-loading">Loading team…</div>;
  if (team.error || !team.data) {
    return (
      <div className="page">
        <p className="error-msg">{team.error ?? 'Team not found'}</p>
        <Link to="/teams">← Back to teams</Link>
      </div>
    );
  }

  return (
    <div className="page">
      <Link to="/teams" className="back-link">← All teams</Link>
      <div className="team-header">
        <span className="team-card-logo large">{team.data.logo}</span>
        <div>
          <h1>{team.data.name}</h1>
        </div>
      </div>

      <section className="section">
        <h2>Squad</h2>
        {players.loading ? (
          <p>Loading players…</p>
        ) : (players.data?.length ?? 0) === 0 ? (
          <p className="empty-state">No players assigned yet.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Position</th>
                  <th>Captain</th>
                </tr>
              </thead>
              <tbody>
                {players.data!
                  .sort((a, b) => a.jerseyNumber - b.jerseyNumber)
                  .map((p) => (
                    <tr key={p.id}>
                      <td>{p.jerseyNumber}</td>
                      <td>{p.name}</td>
                      <td>{p.position}</td>
                      <td>{p.isCaptain ? '©' : ''}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
