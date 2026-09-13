import { Link } from 'react-router-dom';
import * as api from '../api/client';
import { useAsyncData } from '../hooks/useAsyncData';

export function TeamsPage() {
  const { data: teams, loading, error } = useAsyncData(() => api.getTeams(), []);

  if (loading) return <div className="page-loading">Loading teams…</div>;

  return (
    <div className="page">
      <h1>Teams</h1>
      {error && <p className="error-msg">{error}</p>}
      <div className="team-grid">
        {(teams ?? []).map((team) => (
          <Link key={team.id} to={`/teams/${team.id}`} className="team-card">
            <span className="team-card-logo">{team.logo}</span>
            <h2>{team.name}</h2>
          </Link>
        ))}
      </div>
    </div>
  );
}
