/**
 * Central API client — all backend calls go through here.
 * Backed by the FastAPI backend running at http://localhost:8000.
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

const BASE_URL = 'http://localhost:8000';
const TOKEN_KEY = 'scoreboard-token';

// ─── Token storage ────────────────────────────────────────────────────────────

function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ─── HTTP helper ──────────────────────────────────────────────────────────────

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) {
    return undefined as T;
  }

  const data: unknown = await res.json();

  if (!res.ok) {
    const msg =
      (data as { message?: string; detail?: string })?.message ??
      (data as { message?: string; detail?: string })?.detail ??
      `HTTP ${res.status}`;
    throw new Error(String(msg));
  }

  return data as T;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export async function login(credentials: LoginCredentials): Promise<AuthUser> {
  const res = await request<{ email: string; token: string }>(
    'POST',
    '/auth/login',
    credentials,
  );
  setToken(res.token);
  return { email: res.email };
}

export async function logout(): Promise<void> {
  await request<void>('POST', '/auth/logout');
  clearToken();
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  try {
    const user = await request<AuthUser | null>('GET', '/auth/me');
    return user ?? null;
  } catch {
    clearToken();
    return null;
  }
}

// ─── League ───────────────────────────────────────────────────────────────────

export async function getLeague(): Promise<League> {
  return request<League>('GET', '/league');
}

export async function updateLeague(input: UpdateLeagueInput): Promise<League> {
  return request<League>('PATCH', '/league', input);
}

// ─── Teams ────────────────────────────────────────────────────────────────────

export async function getTeams(): Promise<Team[]> {
  return request<Team[]>('GET', '/teams');
}

export async function getTeam(id: string): Promise<Team> {
  return request<Team>('GET', `/teams/${id}`);
}

export async function createTeam(input: CreateTeamInput): Promise<Team> {
  return request<Team>('POST', '/teams', input);
}

export async function updateTeam(
  id: string,
  input: UpdateTeamInput,
): Promise<Team> {
  return request<Team>('PATCH', `/teams/${id}`, input);
}

export async function deleteTeam(id: string): Promise<void> {
  return request<void>('DELETE', `/teams/${id}`);
}

// ─── Players ──────────────────────────────────────────────────────────────────

export async function getPlayers(teamId?: string): Promise<Player[]> {
  const qs = teamId ? `?teamId=${encodeURIComponent(teamId)}` : '';
  return request<Player[]>('GET', `/players${qs}`);
}

export async function getPlayer(id: string): Promise<Player> {
  return request<Player>('GET', `/players/${id}`);
}

export async function createPlayer(input: CreatePlayerInput): Promise<Player> {
  return request<Player>('POST', '/players', input);
}

export async function updatePlayer(
  id: string,
  input: UpdatePlayerInput,
): Promise<Player> {
  return request<Player>('PATCH', `/players/${id}`, input);
}

export async function deletePlayer(id: string): Promise<void> {
  return request<void>('DELETE', `/players/${id}`);
}

// ─── Matches ──────────────────────────────────────────────────────────────────

export async function getMatches(status?: Match['status']): Promise<Match[]> {
  const qs = status ? `?status=${encodeURIComponent(status)}` : '';
  return request<Match[]>('GET', `/matches${qs}`);
}

export async function getMatch(id: string): Promise<Match> {
  return request<Match>('GET', `/matches/${id}`);
}

export async function createMatch(input: CreateMatchInput): Promise<Match> {
  return request<Match>('POST', '/matches', input);
}

export async function updateMatch(
  id: string,
  input: UpdateMatchInput,
): Promise<Match> {
  return request<Match>('PATCH', `/matches/${id}`, input);
}

export async function startMatch(id: string): Promise<Match> {
  return request<Match>('POST', `/matches/${id}/start`);
}

export async function cancelMatch(id: string): Promise<Match> {
  return request<Match>('POST', `/matches/${id}/cancel`);
}

export async function finishMatch(id: string): Promise<Match> {
  return request<Match>('POST', `/matches/${id}/finish`);
}

// ─── Match Events ─────────────────────────────────────────────────────────────

export async function getMatchEvents(matchId: string): Promise<MatchEvent[]> {
  return request<MatchEvent[]>('GET', `/matches/${matchId}/events`);
}

export async function addMatchEvent(
  matchId: string,
  input: CreateEventInput,
): Promise<MatchEvent> {
  return request<MatchEvent>('POST', `/matches/${matchId}/events`, input);
}

export async function removeMatchEvent(
  matchId: string,
  eventId: string,
): Promise<void> {
  return request<void>('DELETE', `/matches/${matchId}/events/${eventId}`);
}

// ─── Standings ────────────────────────────────────────────────────────────────

export async function getStandings(): Promise<StandingRow[]> {
  return request<StandingRow[]>('GET', '/standings');
}
