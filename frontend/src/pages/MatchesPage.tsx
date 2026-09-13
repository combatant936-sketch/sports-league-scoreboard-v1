import { useState } from 'react';
import * as api from '../api/client';
import { MatchCard } from '../components/MatchCard';
import { useAsyncData } from '../hooks/useAsyncData';
import type { MatchStatus } from '../types';

const tabs: { label: string; value: MatchStatus | 'all' }[] = [
  { label: 'All', value: 'all' },
  { label: 'Upcoming', value: 'scheduled' },
  { label: 'Live', value: 'live' },
  { label: 'Finished', value: 'finished' },
  { label: 'Cancelled', value: 'cancelled' },
];

export function MatchesPage() {
  const [filter, setFilter] = useState<MatchStatus | 'all'>('all');
  const matches = useAsyncData(
    () => (filter === 'all' ? api.getMatches() : api.getMatches(filter)),
    [filter],
  );
  const teams = useAsyncData(() => api.getTeams(), []);

  const teamMap = new Map((teams.data ?? []).map((t) => [t.id, t]));

  return (
    <div className="page">
      <h1>Matches</h1>
      <div className="tab-bar">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            type="button"
            className={`tab ${filter === tab.value ? 'active' : ''}`}
            onClick={() => setFilter(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {matches.loading ? (
        <div className="page-loading">Loading matches…</div>
      ) : matches.error ? (
        <p className="error-msg">{matches.error}</p>
      ) : (matches.data?.length ?? 0) === 0 ? (
        <p className="empty-state">No matches in this category.</p>
      ) : (
        <div className="match-grid">
          {matches.data!.map((m) => (
            <MatchCard key={m.id} match={m} teams={teamMap} linkTo={`/matches/${m.id}`} />
          ))}
        </div>
      )}
    </div>
  );
}
