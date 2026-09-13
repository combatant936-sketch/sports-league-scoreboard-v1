import * as api from '../api/client';
import { MatchCard } from '../components/MatchCard';
import { StandingsTable } from '../components/StandingsTable';
import { useAsyncData } from '../hooks/useAsyncData';

export function HomePage() {
  const league = useAsyncData(() => api.getLeague(), []);
  const standings = useAsyncData(() => api.getStandings(), []);
  const teams = useAsyncData(() => api.getTeams(), []);
  const liveMatches = useAsyncData(() => api.getMatches('live'), []);
  const upcoming = useAsyncData(() => api.getMatches('scheduled'), []);

  const loading =
    league.loading || standings.loading || teams.loading;

  if (loading) return <div className="page-loading">Loading league…</div>;

  const teamMap = new Map((teams.data ?? []).map((t) => [t.id, t]));

  return (
    <div className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">{league.data?.season} Season</p>
          <h1>{league.data?.name}</h1>
          <p className="hero-meta">
            Status: <span className={`league-status status-${league.data?.status}`}>{league.data?.status}</span>
          </p>
        </div>
      </section>

      {(liveMatches.data?.length ?? 0) > 0 && (
        <section className="section">
          <h2>Live Now</h2>
          <div className="match-grid">
            {liveMatches.data!.map((m) => (
              <MatchCard key={m.id} match={m} teams={teamMap} linkTo={`/matches/${m.id}`} />
            ))}
          </div>
        </section>
      )}

      <section className="section">
        <h2>Standings</h2>
        {standings.error ? (
          <p className="error-msg">{standings.error}</p>
        ) : (
          <StandingsTable standings={standings.data ?? []} />
        )}
      </section>

      <section className="section">
        <h2>Upcoming Matches</h2>
        {(upcoming.data?.length ?? 0) === 0 ? (
          <p className="empty-state">No upcoming matches scheduled.</p>
        ) : (
          <div className="match-grid">
            {upcoming.data!.slice(0, 4).map((m) => (
              <MatchCard key={m.id} match={m} teams={teamMap} linkTo={`/matches/${m.id}`} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
