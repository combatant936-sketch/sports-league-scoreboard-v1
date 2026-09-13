import { Link } from 'react-router-dom';
import * as api from '../../api/client';
import { StandingsTable } from '../../components/StandingsTable';
import { useAsyncData } from '../../hooks/useAsyncData';
import { useAuth } from '../../hooks/useAuth';

export function AdminDashboard() {
  const { logout } = useAuth();
  const league = useAsyncData(() => api.getLeague(), []);
  const teams = useAsyncData(() => api.getTeams(), []);
  const players = useAsyncData(() => api.getPlayers(), []);
  const matches = useAsyncData(() => api.getMatches(), []);
  const standings = useAsyncData(() => api.getStandings(), []);

  const liveCount = matches.data?.filter((m) => m.status === 'live').length ?? 0;
  const scheduledCount = matches.data?.filter((m) => m.status === 'scheduled').length ?? 0;

  return (
    <div className="page admin-page">
      <div className="admin-page-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p>{league.data?.name} — {league.data?.season}</p>
        </div>
        <button type="button" className="btn secondary" onClick={() => logout()}>
          Logout
        </button>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-value">{teams.data?.length ?? 0}</span>
          <span className="stat-label">Teams</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{players.data?.length ?? 0}</span>
          <span className="stat-label">Players</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{liveCount}</span>
          <span className="stat-label">Live matches</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{scheduledCount}</span>
          <span className="stat-label">Upcoming</span>
        </div>
      </div>

      <div className="quick-links">
        <Link to="/admin/teams" className="btn secondary">Manage teams</Link>
        <Link to="/admin/players" className="btn secondary">Manage players</Link>
        <Link to="/admin/matches" className="btn secondary">Manage matches</Link>
        <Link to="/admin/league" className="btn secondary">Edit league</Link>
      </div>

      <section className="section">
        <h2>Current Standings</h2>
        <StandingsTable standings={standings.data ?? []} />
      </section>
    </div>
  );
}
