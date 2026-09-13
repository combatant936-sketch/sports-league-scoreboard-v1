import { useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import * as api from '../../api/client';
import { EventTimeline } from '../../components/EventTimeline';
import { Modal } from '../../components/Modal';
import { StatusBadge } from '../../components/StatusBadge';
import { useAsyncData } from '../../hooks/useAsyncData';
import type { EventType } from '../../types';

const eventTypes: { value: EventType; label: string }[] = [
  { value: 'goal', label: 'Goal' },
  { value: 'yellow_card', label: 'Yellow card' },
  { value: 'red_card', label: 'Red card' },
  { value: 'substitution', label: 'Substitution' },
];

export function AdminMatchManagePage() {
  const { id } = useParams<{ id: string }>();
  const match = useAsyncData(() => api.getMatch(id!), [id]);
  const teams = useAsyncData(() => api.getTeams(), []);
  const events = useAsyncData(() => api.getMatchEvents(id!), [id]);
  const allPlayers = useAsyncData(() => api.getPlayers(), []);

  const [showEventModal, setShowEventModal] = useState(false);
  const [eventType, setEventType] = useState<EventType>('goal');
  const [teamId, setTeamId] = useState('');
  const [playerId, setPlayerId] = useState('');
  const [playerInId, setPlayerInId] = useState('');
  const [playerOutId, setPlayerOutId] = useState('');
  const [minute, setMinute] = useState(1);
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (match.loading) return <div className="page-loading">Loading match…</div>;
  if (match.error || !match.data) {
    return (
      <div className="page admin-page">
        <p className="error-msg">{match.error ?? 'Match not found'}</p>
        <Link to="/admin/matches">← Back</Link>
      </div>
    );
  }

  const m = match.data;
  const teamMap = new Map((teams.data ?? []).map((t) => [t.id, t]));
  const playerMap = new Map((allPlayers.data ?? []).map((p) => [p.id, p]));
  const home = teamMap.get(m.homeTeamId);
  const away = teamMap.get(m.awayTeamId);

  const matchTeamIds = [m.homeTeamId, m.awayTeamId];
  const teamPlayers = (allPlayers.data ?? []).filter((p) => p.teamId === teamId);

  function openEventModal() {
    setEventType('goal');
    setTeamId(m.homeTeamId);
    setPlayerId('');
    setPlayerInId('');
    setPlayerOutId('');
    setMinute(1);
    setDescription('');
    setError(null);
    setShowEventModal(true);
  }

  async function handleAddEvent(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.addMatchEvent(id!, {
        teamId,
        playerId,
        eventType,
        minute,
        description,
        playerInId: eventType === 'substitution' ? playerInId : undefined,
        playerOutId: eventType === 'substitution' ? playerOutId : undefined,
      });
      setShowEventModal(false);
      match.reload();
      events.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRemoveEvent(eventId: string) {
    if (!confirm('Remove this event?')) return;
    try {
      await api.removeMatchEvent(id!, eventId);
      match.reload();
      events.reload();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed');
    }
  }

  async function handleFinish() {
    if (!confirm('Finish this match?')) return;
    try {
      await api.finishMatch(id!);
      match.reload();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed');
    }
  }

  if (m.status !== 'live') {
    return (
      <div className="page admin-page">
        <Link to="/admin/matches" className="back-link">← Matches</Link>
        <p className="error-msg">This match is not live. Only live matches can be managed here.</p>
        <Link to={`/matches/${m.id}`}>View public match page</Link>
      </div>
    );
  }

  return (
    <div className="page admin-page">
      <Link to="/admin/matches" className="back-link">← Matches</Link>

      <div className="admin-page-header">
        <div>
          <StatusBadge status={m.status} />
          <h1>Live Match</h1>
        </div>
        <div className="header-actions">
          <button type="button" className="btn primary" onClick={openEventModal}>
            + Add event
          </button>
          <button type="button" className="btn secondary" onClick={handleFinish}>
            Finish match
          </button>
        </div>
      </div>

      <div className="match-detail-scoreboard">
        <div className="match-detail-team">
          <span className="team-card-logo large">{home?.logo}</span>
          <h2>{home?.name}</h2>
        </div>
        <div className="match-detail-score">
          <span className="score-large live-pulse">
            {m.homeScore} – {m.awayScore}
          </span>
        </div>
        <div className="match-detail-team">
          <span className="team-card-logo large">{away?.logo}</span>
          <h2>{away?.name}</h2>
        </div>
      </div>

      <section className="section">
        <h2>Events</h2>
        <EventTimeline events={events.data ?? []} players={playerMap} />
        <ul className="event-admin-list">
          {(events.data ?? []).map((event) => (
            <li key={event.id}>
              <span>{event.minute}&apos; — {event.eventType}</span>
              <button
                type="button"
                className="btn small danger"
                onClick={() => handleRemoveEvent(event.id)}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      </section>

      {showEventModal && (
        <Modal title="Add match event" onClose={() => setShowEventModal(false)}>
          <form onSubmit={handleAddEvent} className="form">
            <label>
              Event type
              <select value={eventType} onChange={(e) => setEventType(e.target.value as EventType)}>
                {eventTypes.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </label>
            <label>
              Team
              <select
                value={teamId}
                onChange={(e) => {
                  setTeamId(e.target.value);
                  setPlayerId('');
                  setPlayerInId('');
                  setPlayerOutId('');
                }}
                required
              >
                {matchTeamIds.map((tid) => {
                  const t = teamMap.get(tid);
                  return <option key={tid} value={tid}>{t?.name}</option>;
                })}
              </select>
            </label>
            <label>
              {eventType === 'substitution' ? 'Player (for record)' : 'Player'}
              <select value={playerId} onChange={(e) => setPlayerId(e.target.value)} required>
                <option value="">Select player</option>
                {teamPlayers.map((p) => (
                  <option key={p.id} value={p.id}>#{p.jerseyNumber} {p.name}</option>
                ))}
              </select>
            </label>
            {eventType === 'substitution' && (
              <>
                <label>
                  Player out
                  <select value={playerOutId} onChange={(e) => setPlayerOutId(e.target.value)} required>
                    <option value="">Select player</option>
                    {teamPlayers.map((p) => (
                      <option key={p.id} value={p.id}>#{p.jerseyNumber} {p.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Player in
                  <select value={playerInId} onChange={(e) => setPlayerInId(e.target.value)} required>
                    <option value="">Select player</option>
                    {teamPlayers.map((p) => (
                      <option key={p.id} value={p.id}>#{p.jerseyNumber} {p.name}</option>
                    ))}
                  </select>
                </label>
              </>
            )}
            <label>
              Minute
              <input
                type="number"
                min={1}
                max={120}
                value={minute}
                onChange={(e) => setMinute(Number(e.target.value))}
                required
              />
            </label>
            <label>
              Description (optional)
              <input value={description} onChange={(e) => setDescription(e.target.value)} />
            </label>
            {error && <p className="error-msg">{error}</p>}
            <div className="form-actions">
              <button type="button" className="btn secondary" onClick={() => setShowEventModal(false)}>
                Cancel
              </button>
              <button type="submit" className="btn primary" disabled={submitting}>
                {submitting ? 'Adding…' : 'Add event'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
