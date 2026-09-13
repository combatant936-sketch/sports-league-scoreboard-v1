import { useState, type FormEvent } from 'react';
import * as api from '../../api/client';
import { Modal } from '../../components/Modal';
import { useAsyncData } from '../../hooks/useAsyncData';
import type { Team } from '../../types';

export function AdminTeamsPage() {
  const teams = useAsyncData(() => api.getTeams(), []);
  const [modal, setModal] = useState<'create' | 'edit' | null>(null);
  const [editing, setEditing] = useState<Team | null>(null);
  const [name, setName] = useState('');
  const [logo, setLogo] = useState('⚽');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function openCreate() {
    setName('');
    setLogo('⚽');
    setError(null);
    setEditing(null);
    setModal('create');
  }

  function openEdit(team: Team) {
    setName(team.name);
    setLogo(team.logo);
    setError(null);
    setEditing(team);
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
      if (modal === 'create') {
        await api.createTeam({ name, logo });
      } else if (editing) {
        await api.updateTeam(editing.id, { name, logo });
      }
      closeModal();
      teams.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(team: Team) {
    if (!confirm(`Delete ${team.name}?`)) return;
    try {
      await api.deleteTeam(team.id);
      teams.reload();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Delete failed');
    }
  }

  return (
    <div className="page admin-page">
      <div className="admin-page-header">
        <h1>Teams</h1>
        <button type="button" className="btn primary" onClick={openCreate}>
          + Add team
        </button>
      </div>

      {teams.loading ? (
        <p>Loading…</p>
      ) : (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Logo</th>
                <th>Name</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(teams.data ?? []).map((team) => (
                <tr key={team.id}>
                  <td className="logo-cell">{team.logo}</td>
                  <td>{team.name}</td>
                  <td className="actions-cell">
                    <button type="button" className="btn small" onClick={() => openEdit(team)}>
                      Edit
                    </button>
                    <button type="button" className="btn small danger" onClick={() => handleDelete(team)}>
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
        <Modal title={modal === 'create' ? 'Create team' : 'Edit team'} onClose={closeModal}>
          <form onSubmit={handleSubmit} className="form">
            <label>
              Name
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <label>
              Logo (emoji)
              <input value={logo} onChange={(e) => setLogo(e.target.value)} maxLength={4} />
            </label>
            {error && <p className="error-msg">{error}</p>}
            <div className="form-actions">
              <button type="button" className="btn secondary" onClick={closeModal}>
                Cancel
              </button>
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
