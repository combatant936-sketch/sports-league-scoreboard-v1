import { Link } from 'react-router-dom';
import type { Match, Team } from '../types';
import { StatusBadge } from './StatusBadge';

interface MatchCardProps {
  match: Match;
  teams: Map<string, Team>;
  linkTo?: string;
}

export function MatchCard({ match, teams, linkTo }: MatchCardProps) {
  const home = teams.get(match.homeTeamId);
  const away = teams.get(match.awayTeamId);
  const content = (
    <div className="match-card">
      <div className="match-card-header">
        <StatusBadge status={match.status} />
        <time>{new Date(match.scheduledAt).toLocaleString()}</time>
      </div>
      <div className="match-scoreboard">
        <div className="match-team home">
          <span className="team-logo">{home?.logo ?? '?'}</span>
          <span className="team-name">{home?.name ?? 'Unknown'}</span>
        </div>
        <div className="match-score">
          {match.status === 'scheduled' || match.status === 'cancelled' ? (
            <span className="vs">vs</span>
          ) : (
            <span>
              {match.homeScore} – {match.awayScore}
            </span>
          )}
        </div>
        <div className="match-team away">
          <span className="team-logo">{away?.logo ?? '?'}</span>
          <span className="team-name">{away?.name ?? 'Unknown'}</span>
        </div>
      </div>
    </div>
  );

  if (linkTo) {
    return (
      <Link to={linkTo} className="match-card-link">
        {content}
      </Link>
    );
  }
  return content;
}
