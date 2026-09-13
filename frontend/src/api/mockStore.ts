import type {
  League,
  Match,
  MatchEvent,
  Player,
  Team,
} from '../types';

const STORAGE_KEY = 'scoreboard-mock-data';

export interface MockData {
  league: League;
  teams: Team[];
  players: Player[];
  matches: Match[];
  events: MatchEvent[];
  authToken: string | null;
}

const defaultData: MockData = {
  league: {
    id: 'league-1',
    name: 'Premier City League',
    season: '2025/26',
    status: 'active',
  },
  teams: [
    { id: 'team-1', name: 'North United', logo: '⚽', leagueId: 'league-1' },
    { id: 'team-2', name: 'South City FC', logo: '🦁', leagueId: 'league-1' },
    { id: 'team-3', name: 'East Rovers', logo: '🦅', leagueId: 'league-1' },
    { id: 'team-4', name: 'West Athletic', logo: '🐺', leagueId: 'league-1' },
  ],
  players: [
    { id: 'player-1', name: 'Alex Morgan', jerseyNumber: 1, position: 'GK', isCaptain: false, teamId: 'team-1' },
    { id: 'player-2', name: 'Jordan Lee', jerseyNumber: 9, position: 'FWD', isCaptain: true, teamId: 'team-1' },
    { id: 'player-3', name: 'Sam Rivera', jerseyNumber: 10, position: 'MID', isCaptain: false, teamId: 'team-1' },
    { id: 'player-4', name: 'Chris Park', jerseyNumber: 1, position: 'GK', isCaptain: false, teamId: 'team-2' },
    { id: 'player-5', name: 'Taylor Brooks', jerseyNumber: 7, position: 'FWD', isCaptain: true, teamId: 'team-2' },
    { id: 'player-6', name: 'Morgan Ellis', jerseyNumber: 6, position: 'MID', isCaptain: false, teamId: 'team-2' },
    { id: 'player-7', name: 'Riley Chen', jerseyNumber: 11, position: 'FWD', isCaptain: true, teamId: 'team-3' },
    { id: 'player-8', name: 'Casey Wright', jerseyNumber: 4, position: 'DEF', isCaptain: false, teamId: 'team-3' },
    { id: 'player-9', name: 'Jamie Fox', jerseyNumber: 8, position: 'MID', isCaptain: true, teamId: 'team-4' },
    { id: 'player-10', name: 'Drew Stone', jerseyNumber: 3, position: 'DEF', isCaptain: false, teamId: 'team-4' },
  ],
  matches: [
    {
      id: 'match-1',
      homeTeamId: 'team-1',
      awayTeamId: 'team-2',
      scheduledAt: '2026-09-10T15:00:00.000Z',
      status: 'finished',
      homeScore: 2,
      awayScore: 1,
    },
    {
      id: 'match-2',
      homeTeamId: 'team-3',
      awayTeamId: 'team-4',
      scheduledAt: '2026-09-11T15:00:00.000Z',
      status: 'finished',
      homeScore: 1,
      awayScore: 1,
    },
    {
      id: 'match-3',
      homeTeamId: 'team-1',
      awayTeamId: 'team-3',
      scheduledAt: '2026-09-20T14:00:00.000Z',
      status: 'scheduled',
      homeScore: 0,
      awayScore: 0,
    },
    {
      id: 'match-4',
      homeTeamId: 'team-2',
      awayTeamId: 'team-4',
      scheduledAt: '2026-09-21T16:30:00.000Z',
      status: 'scheduled',
      homeScore: 0,
      awayScore: 0,
    },
  ],
  events: [
    {
      id: 'event-1',
      matchId: 'match-1',
      teamId: 'team-1',
      playerId: 'player-2',
      eventType: 'goal',
      minute: 23,
      description: 'Header from corner',
    },
    {
      id: 'event-2',
      matchId: 'match-1',
      teamId: 'team-2',
      playerId: 'player-5',
      eventType: 'goal',
      minute: 41,
      description: 'Penalty kick',
    },
    {
      id: 'event-3',
      matchId: 'match-1',
      teamId: 'team-1',
      playerId: 'player-3',
      eventType: 'goal',
      minute: 78,
      description: 'Long-range strike',
    },
    {
      id: 'event-4',
      matchId: 'match-1',
      teamId: 'team-2',
      playerId: 'player-6',
      eventType: 'yellow_card',
      minute: 55,
      description: 'Late tackle',
    },
    {
      id: 'event-5',
      matchId: 'match-2',
      teamId: 'team-3',
      playerId: 'player-7',
      eventType: 'goal',
      minute: 12,
      description: 'Tap-in',
    },
    {
      id: 'event-6',
      matchId: 'match-2',
      teamId: 'team-4',
      playerId: 'player-9',
      eventType: 'goal',
      minute: 67,
      description: 'Free kick',
    },
  ],
  authToken: null,
};

let data: MockData = loadData();

function loadData(): MockData {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return JSON.parse(stored) as MockData;
  } catch {
    /* use defaults */
  }
  return structuredClone(defaultData);
}

function persist(): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function getStore(): MockData {
  return data;
}

export function updateStore(updater: (draft: MockData) => void): MockData {
  updater(data);
  persist();
  return data;
}

export function resetStore(): void {
  data = structuredClone(defaultData);
  persist();
}

export function nextId(prefix: string): string {
  return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
}

export function recalculateMatchScore(matchId: string): void {
  const match = data.matches.find((m) => m.id === matchId);
  if (!match) return;

  const goals = data.events.filter(
    (e) => e.matchId === matchId && e.eventType === 'goal',
  );

  match.homeScore = goals.filter((g) => g.teamId === match.homeTeamId).length;
  match.awayScore = goals.filter((g) => g.teamId === match.awayTeamId).length;
}

export const ADMIN_CREDENTIALS = {
  email: 'admin@league.com',
  password: 'admin123',
};
