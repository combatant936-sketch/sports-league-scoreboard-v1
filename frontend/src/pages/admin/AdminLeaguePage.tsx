import { useEffect, useState, type FormEvent } from 'react';
import * as api from '../../api/client';
import { useAsyncData } from '../../hooks/useAsyncData';
import type { LeagueStatus } from '../../types';

export function AdminLeaguePage() {
  const league = useAsyncData(() => api.getLeague(), []);
  const [name, setName] = useState('');
  const [season, setSeason] = useState('');
  const [status, setStatus] = useState<LeagueStatus>('active');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (league.data) {
      setName(league.data.name);
      setSeason(league.data.season);
      setStatus(league.data.status);
    }
  }, [league.data]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      await api.updateLeague({ name, season, status });
      setMessage('League updated.');
      league.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed');
    } finally {
      setSaving(false);
    }
  }

  if (league.loading) return <div className="page-loading">Loading…</div>;

  return (
    <div className="page admin-page">
      <h1>League Settings</h1>
      <form onSubmit={handleSubmit} className="form card-form">
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Season
          <input value={season} onChange={(e) => setSeason(e.target.value)} required />
        </label>
        <label>
          Status
          <select value={status} onChange={(e) => setStatus(e.target.value as LeagueStatus)}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="completed">Completed</option>
          </select>
        </label>
        {error && <p className="error-msg">{error}</p>}
        {message && <p className="success-msg">{message}</p>}
        <button type="submit" className="btn primary" disabled={saving}>
          {saving ? 'Saving…' : 'Save changes'}
        </button>
      </form>
    </div>
  );
}
