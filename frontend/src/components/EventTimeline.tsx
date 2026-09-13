import type { MatchEvent, Player } from '../types';

const eventIcons: Record<MatchEvent['eventType'], string> = {
  goal: '⚽',
  yellow_card: '🟨',
  red_card: '🟥',
  substitution: '🔄',
};

const eventLabels: Record<MatchEvent['eventType'], string> = {
  goal: 'Goal',
  yellow_card: 'Yellow card',
  red_card: 'Red card',
  substitution: 'Substitution',
};

interface EventTimelineProps {
  events: MatchEvent[];
  players: Map<string, Player>;
}

export function EventTimeline({ events, players }: EventTimelineProps) {
  if (events.length === 0) {
    return <p className="empty-state">No events recorded yet.</p>;
  }

  return (
    <ul className="event-timeline">
      {events.map((event) => {
        const player = players.get(event.playerId);
        const playerIn = event.playerInId ? players.get(event.playerInId) : null;
        const playerOut = event.playerOutId ? players.get(event.playerOutId) : null;

        return (
          <li key={event.id} className={`event-item event-${event.eventType}`}>
            <span className="event-minute">{event.minute}&apos;</span>
            <span className="event-icon">{eventIcons[event.eventType]}</span>
            <div className="event-details">
              <strong>{eventLabels[event.eventType]}</strong>
              {event.eventType === 'substitution' ? (
                <span>
                  {playerOut?.name ?? '?'} → {playerIn?.name ?? '?'}
                </span>
              ) : (
                <span>{player?.name ?? 'Unknown player'}</span>
              )}
              {event.description && <em>{event.description}</em>}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
