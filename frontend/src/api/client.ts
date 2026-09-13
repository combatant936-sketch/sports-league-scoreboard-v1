/**
 * Central API client — all backend calls go through here.
 * Currently backed by an in-memory mock store (localStorage).
 * Swap implementations here when the real backend is ready.
 */

import type {
  AuthUser,
  CreateEventInput,
  CreateMatchInput,
  CreatePlayerInput,
  CreateTeamInput,
  League,
  LoginCredentials,
  Match,
  MatchEvent,
  Player,
  StandingRow,
  Team,
  UpdateLeagueInput,
  UpdateMatchInput,
  UpdatePlayerInput,
  UpdateTeamInput,
} from '../types';
import { calculateStandings } from '../utils/standings';
import {
  ADMIN_CREDENTIALS,
  getStore,
  nextId,
  recalculateMatchScore,
  updateStore,
} from './mockStore';

const MOCK_DELAY_MS = 200;

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), MOCK_DELAY_MS));
}

function requireAuth(): void {
  if (!getStore().authToken) {
    throw new Error('Unauthorized');
  }
}

function getTeamOrThrow(teamId: string): Team {
  const team = getStore().teams.find((t) => t.id === teamId);
  if (!team) throw new Error('Team not found');
  return team;
}

function getMatchOrThrow(matchId: string): Match {
  const match = getStore().matches.find((m) => m.id === matchId);
  if (!match) throw new Error('Match not found');
  return match;
}

function getPlayerOrThrow(playerId: string): Player {
  const player = getStore().players.find((p) => p.id === playerId);
  if (!player) throw new Error('Player not found');
  return player;
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export async function login(credentials: LoginCredentials): Promise<AuthUser> {
  const { email, password } = credentials;
  if (
    email !== ADMIN_CREDENTIALS.email ||
    password !== ADMIN_CREDENTIALS.password
  ) {
    throw new Error('Invalid email or password');
  }
  updateStore((draft) => {
    draft.authToken = `token-${crypto.randomUUID()}`;
  });
  return delay({ email });
}

export async function logout(): Promise<void> {
  updateStore((draft) => {
    draft.authToken = null;
  });
  return delay(undefined);
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const token = getStore().authToken;
  if (!token) return delay(null);
  return delay({ email: ADMIN_CREDENTIALS.email });
}

// ─── League ──────────────────────────────────────────────────────────────────

export async function getLeague(): Promise<League> {
  return delay(getStore().league);
}

export async function updateLeague(input: UpdateLeagueInput): Promise<League> {
  requireAuth();
  updateStore((draft) => {
    draft.league = { ...draft.league, ...input };
  });
  return delay(getStore().league);
}

// ─── Teams ───────────────────────────────────────────────────────────────────

export async function getTeams(): Promise<Team[]> {
  return delay([...getStore().teams]);
}

export async function getTeam(id: string): Promise<Team> {
  return delay(getTeamOrThrow(id));
}

export async function createTeam(input: CreateTeamInput): Promise<Team> {
  requireAuth();
  const team: Team = {
    id: nextId('team'),
    name: input.name,
    logo: input.logo,
    leagueId: getStore().league.id,
  };
  updateStore((draft) => {
    draft.teams.push(team);
  });
  return delay(team);
}

export async function updateTeam(id: string, input: UpdateTeamInput): Promise<Team> {
  requireAuth();
  updateStore((draft) => {
    const idx = draft.teams.findIndex((t) => t.id === id);
    if (idx === -1) throw new Error('Team not found');
    draft.teams[idx] = { ...draft.teams[idx], ...input };
  });
  return delay(getTeamOrThrow(id));
}

export async function deleteTeam(id: string): Promise<void> {
  requireAuth();
  const hasPlayers = getStore().players.some((p) => p.teamId === id);
  if (hasPlayers) throw new Error('Cannot delete team with assigned players');
  const inMatch = getStore().matches.some(
    (m) => m.homeTeamId === id || m.awayTeamId === id,
  );
  if (inMatch) throw new Error('Cannot delete team referenced in matches');
  updateStore((draft) => {
    draft.teams = draft.teams.filter((t) => t.id !== id);
  });
  return delay(undefined);
}

// ─── Players ─────────────────────────────────────────────────────────────────

export async function getPlayers(teamId?: string): Promise<Player[]> {
  const players = getStore().players;
  const filtered = teamId ? players.filter((p) => p.teamId === teamId) : players;
  return delay([...filtered]);
}

export async function getPlayer(id: string): Promise<Player> {
  return delay(getPlayerOrThrow(id));
}

export async function createPlayer(input: CreatePlayerInput): Promise<Player> {
  requireAuth();
  getTeamOrThrow(input.teamId);
  const player: Player = { id: nextId('player'), ...input };
  updateStore((draft) => {
    if (player.isCaptain) {
      for (const p of draft.players) {
        if (p.teamId === player.teamId) p.isCaptain = false;
      }
    }
    draft.players.push(player);
  });
  return delay(player);
}

export async function updatePlayer(id: string, input: UpdatePlayerInput): Promise<Player> {
  requireAuth();
  if (input.teamId) getTeamOrThrow(input.teamId);
  updateStore((draft) => {
    const idx = draft.players.findIndex((p) => p.id === id);
    if (idx === -1) throw new Error('Player not found');
    const updated = { ...draft.players[idx], ...input };
    if (updated.isCaptain) {
      for (const p of draft.players) {
        if (p.teamId === updated.teamId && p.id !== id) p.isCaptain = false;
      }
    }
    draft.players[idx] = updated;
  });
  return delay(getPlayerOrThrow(id));
}

export async function deletePlayer(id: string): Promise<void> {
  requireAuth();
  const inEvent = getStore().events.some(
    (e) => e.playerId === id || e.playerInId === id || e.playerOutId === id,
  );
  if (inEvent) throw new Error('Cannot delete player referenced in match events');
  updateStore((draft) => {
    draft.players = draft.players.filter((p) => p.id !== id);
  });
  return delay(undefined);
}

// ─── Matches ─────────────────────────────────────────────────────────────────

export async function getMatches(status?: Match['status']): Promise<Match[]> {
  let matches = [...getStore().matches];
  if (status) matches = matches.filter((m) => m.status === status);
  matches.sort(
    (a, b) => new Date(b.scheduledAt).getTime() - new Date(a.scheduledAt).getTime(),
  );
  return delay(matches);
}

export async function getMatch(id: string): Promise<Match> {
  return delay(getMatchOrThrow(id));
}

export async function createMatch(input: CreateMatchInput): Promise<Match> {
  requireAuth();
  if (input.homeTeamId === input.awayTeamId) {
    throw new Error('Home and away teams must be different');
  }
  getTeamOrThrow(input.homeTeamId);
  getTeamOrThrow(input.awayTeamId);
  const match: Match = {
    id: nextId('match'),
    homeTeamId: input.homeTeamId,
    awayTeamId: input.awayTeamId,
    scheduledAt: input.scheduledAt,
    status: 'scheduled',
    homeScore: 0,
    awayScore: 0,
  };
  updateStore((draft) => {
    draft.matches.push(match);
  });
  return delay(match);
}

export async function updateMatch(id: string, input: UpdateMatchInput): Promise<Match> {
  requireAuth();
  const match = getMatchOrThrow(id);
  if (match.status !== 'scheduled') {
    throw new Error('Only scheduled matches can be updated');
  }
  if (input.homeTeamId) getTeamOrThrow(input.homeTeamId);
  if (input.awayTeamId) getTeamOrThrow(input.awayTeamId);
  updateStore((draft) => {
    const idx = draft.matches.findIndex((m) => m.id === id);
    if (idx === -1) throw new Error('Match not found');
    draft.matches[idx] = { ...draft.matches[idx], ...input };
  });
  return delay(getMatchOrThrow(id));
}

export async function startMatch(id: string): Promise<Match> {
  requireAuth();
  const match = getMatchOrThrow(id);
  if (match.status !== 'scheduled') {
    throw new Error('Only scheduled matches can be started');
  }
  updateStore((draft) => {
    const idx = draft.matches.findIndex((m) => m.id === id);
    draft.matches[idx] = { ...draft.matches[idx], status: 'live' };
  });
  return delay(getMatchOrThrow(id));
}

export async function cancelMatch(id: string): Promise<Match> {
  requireAuth();
  const match = getMatchOrThrow(id);
  if (match.status === 'finished') {
    throw new Error('Finished matches cannot be cancelled');
  }
  updateStore((draft) => {
    const idx = draft.matches.findIndex((m) => m.id === id);
    draft.matches[idx] = {
      ...draft.matches[idx],
      status: 'cancelled',
      homeScore: 0,
      awayScore: 0,
    };
    draft.events = draft.events.filter((e) => e.matchId !== id);
  });
  return delay(getMatchOrThrow(id));
}

export async function finishMatch(id: string): Promise<Match> {
  requireAuth();
  const match = getMatchOrThrow(id);
  if (match.status !== 'live') {
    throw new Error('Only live matches can be finished');
  }
  updateStore((draft) => {
    const idx = draft.matches.findIndex((m) => m.id === id);
    draft.matches[idx] = { ...draft.matches[idx], status: 'finished' };
  });
  return delay(getMatchOrThrow(id));
}

// ─── Match Events ────────────────────────────────────────────────────────────

export async function getMatchEvents(matchId: string): Promise<MatchEvent[]> {
  const events = getStore()
    .events.filter((e) => e.matchId === matchId)
    .sort((a, b) => a.minute - b.minute);
  return delay(events);
}

export async function addMatchEvent(
  matchId: string,
  input: CreateEventInput,
): Promise<MatchEvent> {
  requireAuth();
  const match = getMatchOrThrow(matchId);
  if (match.status !== 'live') {
    throw new Error('Events can only be added to live matches');
  }
  getTeamOrThrow(input.teamId);
  getPlayerOrThrow(input.playerId);

  if (input.eventType === 'substitution') {
    if (!input.playerInId || !input.playerOutId) {
      throw new Error('Substitution requires player in and player out');
    }
    getPlayerOrThrow(input.playerInId);
    getPlayerOrThrow(input.playerOutId);
  }

  const event: MatchEvent = {
    id: nextId('event'),
    matchId,
    teamId: input.teamId,
    playerId: input.playerId,
    eventType: input.eventType,
    minute: input.minute,
    description: input.description ?? '',
    playerInId: input.playerInId,
    playerOutId: input.playerOutId,
  };

  updateStore((draft) => {
    draft.events.push(event);
    if (event.eventType === 'goal') {
      recalculateMatchScore(matchId);
    }
  });
  return delay(event);
}

export async function removeMatchEvent(matchId: string, eventId: string): Promise<void> {
  requireAuth();
  const match = getMatchOrThrow(matchId);
  if (match.status !== 'live') {
    throw new Error('Events can only be removed from live matches');
  }
  updateStore((draft) => {
    const event = draft.events.find((e) => e.id === eventId);
    if (!event) throw new Error('Event not found');
    draft.events = draft.events.filter((e) => e.id !== eventId);
    if (event.eventType === 'goal') {
      recalculateMatchScore(matchId);
    }
  });
  return delay(undefined);
}

// ─── Standings ───────────────────────────────────────────────────────────────

export async function getStandings(): Promise<StandingRow[]> {
  const { teams, matches } = getStore();
  return delay(calculateStandings(teams, matches));
}
