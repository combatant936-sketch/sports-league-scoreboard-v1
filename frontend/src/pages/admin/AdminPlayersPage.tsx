import { useState, type FormEvent } from 'react';
import * as api from '../../api/client';
import { Modal } from '../../components/Modal';
import { useAsyncData } from '../../hooks/useAsyncData';
import type { Player, PlayerPosition } from '../../types';

const positions: PlayerPosition[] = ['GK', 'DEF', 'MID', 'FWD'];

export function AdminPlayersPage() {
  const players = useAsyncData(() => api.getPlayers(), []);
  const teams = useAsyncData(() => api.getTeams(), []);
  const [modal, setModal] = useState<'create' | 'edit' | null>(null);
  const [editing, setEditing] = useState<Player | null>(null);
  const [name, setName] = useState('');
  const [jerseyNumber, setJerseyNumber] = useState(1);
  const [position, setPosition] = useState<PlayerPosition>('MID');
  const [isCaptain, setIsCaptain] = useState(false);
  const [teamId, setTeamId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const teamMap = new Map((teams.data ?? []).map((t) => [t.id, t.name]));

  function openCreate() {
    setName('');
    setJerseyNumber(1);
    setPosition('MID');
    setIsCaptain(false);
    setTeamId(teams.data?.[0]?.id ?? '');
    setError(null);
    setEditing(null);
    setModal('create');
  }

  function openEdit(player: Player) {
    setName(player.name);
    setJerseyNumber(player.jerseyNumber);
    setPosition(player.position);
    setIsCaptain(player.isCaptain);
    setTeamId(player.teamId);
    setError(null);
    setEditing(player);
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
    try {
      const input = { name, jerseyNumber, position, isCaptain, teamId };
      if (modal === 'create') {
        await api.createPlayer(input);
      } else if (editing) {
        await api.updatePlayer(editing.id, input);
      }
      closeModal();
      players.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(player: Player) {
    if (!confirm(`Delete ${player.name}?`)) return;
    try {
      await api.deletePlayer(player.id);
      players.reload();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Delete failed');
    }
  }

  return (
    <div className="page admin-page">
      <div className="admin-page-header">
        <h1>Players</h1>
        <button type="button" className="btn primary" onClick={openCreate} disabled={!teams.data?.length}>
          + Add player
        </button>
      </div>

      {players.loading ? (
        <p>Loading…</p>
      ) : (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Position</th>
                <th>Team</th>
                <th>Captain</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(players.data ?? []).map((player) => (
                <tr key={player.id}>
                  <td>{player.jerseyNumber}</td>
                  <td>{player.name}</td>
                  <td>{player.position}</td>
                  <td>{teamMap.get(player.teamId) ?? '—'}</td>
                  <td>{player.isCaptain ? '©' : ''}</td>
                  <td className="actions-cell">
                    <button type="button" className="btn small" onClick={() => openEdit(player)}>
                      Edit
                    </button>
                    <button type="button" className="btn small danger" onClick={() => handleDelete(player)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <Modal title={modal === 'create' ? 'Create player' : 'Edit player'} onClose={closeModal}>
          <form onSubmit={handleSubmit} className="form">
            <label>
              Name
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <label>
              Jersey number
              <input
                type="number"
                min={1}
                max={99}
                value={jerseyNumber}
                onChange={(e) => setJerseyNumber(Number(e.target.value))}
                required
              />
            </label>
            <label>
              Position
              <select value={position} onChange={(e) => setPosition(e.target.value as PlayerPosition)}>
                {positions.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </label>
            <label>
              Team
              <select value={teamId} onChange={(e) => setTeamId(e.target.value)} required>
                {(teams.data ?? []).map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isCaptain}
                onChange={(e) => setIsCaptain(e.target.checked)}
              />
              Team captain
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
