import type { MatchStatus } from '../types';

const labels: Record<MatchStatus, string> = {
  scheduled: 'Scheduled',
  live: 'Live',
  finished: 'Finished',
  cancelled: 'Cancelled',
};

export function StatusBadge({ status }: { status: MatchStatus }) {
  return <span className={`badge badge-${status}`}>{labels[status]}</span>;
}
