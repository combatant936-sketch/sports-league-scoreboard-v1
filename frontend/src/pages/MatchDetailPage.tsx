import { Link, useParams } from 'react-router-dom';
import * as api from '../api/client';
import { EventTimeline } from '../components/EventTimeline';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../hooks/useAsyncData';

export function MatchDetailPage() {
  const { id } = useParams<{ id: string }>();
  const match = useAsyncData(() => api.getMatch(id!), [id]);
  const teams = useAsyncData(() => api.getTeams(), []);
  const events = useAsyncData(() => api.getMatchEvents(id!), [id]);
  const players = useAsyncData(() => api.getPlayers(), []);

  if (match.loading) return <div className="page-loading">Loading match…</div>;
  if (match.error || !match.data) {
    return (
      <div className="page">
        <p className="error-msg">{match.error ?? 'Match not found'}</p>
        <Link to="/matches">← Back to matches</Link>
      </div>
    );
  }

  const teamMap = new Map((teams.data ?? []).map((t) => [t.id, t]));
  const playerMap = new Map((players.data ?? []).map((p) => [p.id, p]));
  const home = teamMap.get(match.data.homeTeamId);
  const away = teamMap.get(match.data.awayTeamId);
  const m = match.data;

  return (
    <div className="page">
      <Link to="/matches" className="back-link">← All matches</Link>

      <div className="match-detail-header">
        <StatusBadge status={m.status} />
        <time>{new Date(m.scheduledAt).toLocaleString()}</time>
      </div>

      <div className="match-detail-scoreboard">
        <div className="match-detail-team">
          <span className="team-card-logo large">{home?.logo}</span>
          <h2>{home?.name}</h2>
        </div>
        <div className="match-detail-score">
          {m.status === 'scheduled' || m.status === 'cancelled' ? (
            <span className="vs large">vs</span>
          ) : (
            <span className="score-large">
              {m.homeScore} – {m.awayScore}
            </span>
          )}
        </div>
        <div className="match-detail-team">
          <span className="team-card-logo large">{away?.logo}</span>
          <h2>{away?.name}</h2>
        </div>
      </div>

      <section className="section">
        <h2>Match Timeline</h2>
        <EventTimeline events={events.data ?? []} players={playerMap} />
      </section>
    </div>
  );
}
