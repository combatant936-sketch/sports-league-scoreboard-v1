export type LeagueStatus = 'active' | 'inactive' | 'completed';

export interface League {
  id: string;
  name: string;
  season: string;
  status: LeagueStatus;
}

export interface Team {
  id: string;
  name: string;
  logo: string;
  leagueId: string;
}

export type PlayerPosition = 'GK' | 'DEF' | 'MID' | 'FWD';

export interface Player {
  id: string;
  name: string;
  jerseyNumber: number;
  position: PlayerPosition;
  isCaptain: boolean;
  teamId: string;
}

export type MatchStatus = 'scheduled' | 'live' | 'finished' | 'cancelled';

export interface Match {
  id: string;
  homeTeamId: string;
  awayTeamId: string;
  scheduledAt: string;
  status: MatchStatus;
  homeScore: number;
  awayScore: number;
}

export type EventType = 'goal' | 'yellow_card' | 'red_card' | 'substitution';

export interface MatchEvent {
  id: string;
  matchId: string;
  teamId: string;
  playerId: string;
  eventType: EventType;
  minute: number;
  description: string;
  playerInId?: string;
  playerOutId?: string;
}

export interface StandingRow {
  position: number;
  teamId: string;
  teamName: string;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
  points: number;
}

export interface AuthUser {
  email: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface CreateTeamInput {
  name: string;
  logo: string;
}

export interface UpdateTeamInput {
  name?: string;
  logo?: string;
}

export interface CreatePlayerInput {
  name: string;
  jerseyNumber: number;
  position: PlayerPosition;
  isCaptain: boolean;
  teamId: string;
}

export interface UpdatePlayerInput {
  name?: string;
  jerseyNumber?: number;
  position?: PlayerPosition;
  isCaptain?: boolean;
  teamId?: string;
}

export interface CreateMatchInput {
  homeTeamId: string;
  awayTeamId: string;
  scheduledAt: string;
}

export interface UpdateMatchInput {
  homeTeamId?: string;
  awayTeamId?: string;
  scheduledAt?: string;
}

export interface CreateEventInput {
  teamId: string;
  playerId: string;
  eventType: EventType;
  minute: number;
  description?: string;
  playerInId?: string;
  playerOutId?: string;
}

export interface UpdateLeagueInput {
  name?: string;
  season?: string;
  status?: LeagueStatus;
}
