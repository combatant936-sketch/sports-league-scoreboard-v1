import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import * as api from '../../api/client';
import { Modal } from '../../components/Modal';
import { StatusBadge } from '../../components/StatusBadge';
import { useAsyncData } from '../../hooks/useAsyncData';
import type { Match } from '../../types';

export function AdminMatchesPage() {
  const matches = useAsyncData(() => api.getMatches(), []);
  const teams = useAsyncData(() => api.getTeams(), []);
  const [modal, setModal] = useState<'create' | 'edit' | null>(null);
  const [editing, setEditing] = useState<Match | null>(null);
  const [homeTeamId, setHomeTeamId] = useState('');
  const [awayTeamId, setAwayTeamId] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const teamMap = new Map((teams.data ?? []).map((t) => [t.id, t.name]));
  const teamList = teams.data ?? [];

  function toLocalInputValue(iso: string): string {
    const d = new Date(iso);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function openCreate() {
    setHomeTeamId(teamList[0]?.id ?? '');
    setAwayTeamId(teamList[1]?.id ?? teamList[0]?.id ?? '');
    setScheduledAt(toLocalInputValue(new Date(Date.now() + 86400000).toISOString()));
    setError(null);
    setEditing(null);
    setModal('create');
  }

  function openEdit(match: Match) {
    setHomeTeamId(match.homeTeamId);
    setAwayTeamId(match.awayTeamId);
    setScheduledAt(toLocalInputValue(match.scheduledAt));
    setError(null);
    setEditing(match);
    setModal('edit');
  }

  function closeModal() {
    setModal(null);
    setEditing(null);
    setError(null);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    const scheduledIso = new Date(scheduledAt).toISOString();
    try {
      if (modal === 'create') {
        await api.createMatch({ homeTeamId, awayTeamId, scheduledAt: scheduledIso });
      } else if (editing) {
        await api.updateMatch(editing.id, { homeTeamId, awayTeamId, scheduledAt: scheduledIso });
      }
      closeModal();
      matches.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAction(match: Match, action: 'start' | 'cancel' | 'finish') {
    const labels = { start: 'Start', cancel: 'Cancel', finish: 'Finish' };
    if (!confirm(`${labels[action]} this match?`)) return;
    try {
      if (action === 'start') await api.startMatch(match.id);
      else if (action === 'cancel') await api.cancelMatch(match.id);
      else await api.finishMatch(match.id);
      matches.reload();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Action failed');
    }
  }

  return (
    <div className="page admin-page">
      <div className="admin-page-header">
        <h1>Matches</h1>
        <button type="button" className="btn primary" onClick={openCreate} disabled={teamList.length < 2}>
          + Schedule match
        </button>
      </div>

      {matches.loading ? (
        <p>Loading…</p>
      ) : (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Home</th>
                <th>Score</th>
                <th>Away</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(matches.data ?? []).map((match) => (
                <tr key={match.id}>
                  <td>{new Date(match.scheduledAt).toLocaleString()}</td>
                  <td>{teamMap.get(match.homeTeamId)}</td>
                  <td className="score-cell">
                    {match.status === 'scheduled' || match.status === 'cancelled'
                      ? '—'
                      : `${match.homeScore} – ${match.awayScore}`}
                  </td>
                  <td>{teamMap.get(match.awayTeamId)}</td>
                  <td><StatusBadge status={match.status} /></td>
                  <td className="actions-cell wrap">
                    {match.status === 'scheduled' && (
                      <>
                        <button type="button" className="btn small" onClick={() => openEdit(match)}>Edit</button>
                        <button type="button" className="btn small success" onClick={() => handleAction(match, 'start')}>Start</button>
                        <button type="button" className="btn small danger" onClick={() => handleAction(match, 'cancel')}>Cancel</button>
                      </>
                    )}
                    {match.status === 'live' && (
                      <>
                        <Link to={`/admin/matches/${match.id}`} className="btn small primary">
                          Manage
                        </Link>
                        <button type="button" className="btn small" onClick={() => handleAction(match, 'finish')}>Finish</button>
                        <button type="button" className="btn small danger" onClick={() => handleAction(match, 'cancel')}>Cancel</button>
                      </>
                    )}
                    {(match.status === 'finished' || match.status === 'cancelled') && (
                      <Link to={`/matches/${match.id}`} className="btn small">View</Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <Modal title={modal === 'create' ? 'Schedule match' : 'Edit match'} onClose={closeModal}>
          <form onSubmit={handleSubmit} className="form">
            <label>
              Home team
              <select value={homeTeamId} onChange={(e) => setHomeTeamId(e.target.value)} required>
                {teamList.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </label>
            <label>
              Away team
              <select value={awayTeamId} onChange={(e) => setAwayTeamId(e.target.value)} required>
                {teamList.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </label>
            <label>
              Date & time
              <input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
                required
              />
            </label>
            {error && <p className="error-msg">{error}</p>}
            <div className="form-actions">
              <button type="button" className="btn secondary" onClick={closeModal}>Cancel</button>
              <button type="submit" className="btn primary" disabled={submitting}>
                {submitting ? 'Saving…' : 'Save'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
