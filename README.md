# ⚽ Sports League Scoreboard

> A modern, full-stack sports league management and real-time scoreboard application. Built with **FastAPI**, **SQLAlchemy 2.0**, **React 19**, **TypeScript**, and **Vite**, featuring a database-agnostic backend, dynamic live scoring, automatic standings calculation, and a role-based admin control portal.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
  - [Public Fan Experience](#public-fan-experience)
  - [Admin Management Portal](#admin-management-portal)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Repository File Structure](#-repository-file-structure)
- [Default Credentials & Seed Data](#-default-credentials--seed-data)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Quickstart (Using Makefile)](#quickstart-using-makefile)
  - [Manual Setup (Without Makefile)](#manual-setup-without-makefile)
- [Database Configuration & Persistence](#-database-configuration--persistence)
  - [Supported Databases](#supported-databases)
  - [Automatic Schema Creation & Seeding](#automatic-schema-creation--seeding)
- [Database Schema & ER Diagram](#-database-schema--er-diagram)
- [Business Logic & Rules](#-business-logic--rules)
  - [Match Lifecycle](#match-lifecycle)
  - [Automatic Scoring & Event Handling](#automatic-scoring--event-handling)
  - [Standings & Tie-Breaking Calculation](#standings--tie-breaking-calculation)
- [REST API Reference & OpenAPI Specification](#-rest-api-reference--openapi-specification)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Makefile Command Reference](#-makefile-command-reference)
- [Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 🌟 Overview

**Sports League Scoreboard** delivers an end-to-end platform for managing and following football leagues. Fans get instantaneous access to live match trackers, goal alerts, player discipline logs, team rosters, and dynamically updated league tables. League administrators have a dedicated, authenticated portal to manage teams, register players, schedule fixtures, and control live matches minute-by-minute with an event logger.

The backend is completely database-agnostic using **SQLAlchemy 2.0 ORM**, running zero-config on **SQLite** for development and easily switched to production relational databases like **PostgreSQL** or **MySQL** via environment variables.

---

## 🚀 Key Features

### Public Fan Experience

- **🏠 League Dashboard & Standings (`/`):**
  - Live league banner displaying current competition name, season, and status.
  - Quick league metrics (registered teams, active players, completed matches).
  - Dynamic Standings Table ranked by points, goal difference, and goals scored.
  - Recent results list with goal breakdowns.
  - Upcoming fixture schedule.
- **⚽ Matches & Schedule Tracker (`/matches`):**
  - Comprehensive fixture list filterable by status (`All`, `Live`, `Scheduled`, `Finished`, `Cancelled`).
  - Score cards with live pulsating badges for in-progress fixtures.
- **⏱️ Match Timeline & Event Center (`/matches/:id`):**
  - Head-to-head scoreboard with team badges and status indicator.
  - Minute-by-minute timeline displaying match events:
    - ⚽ **Goals** with goal scorer identification and optional description.
    - 🟨 **Yellow Cards** and 🟥 **Red Cards** with disciplined player.
    - 🔄 **Substitutions** with incoming and outgoing player details.
- **🛡️ Teams Directory & Squad Rosters (`/teams`, `/teams/:id`):**
  - Team directory overview with team badge emoji, club name, and player counts.
  - Dedicated team detail view with full squad table:
    - Jersey numbers, player names, and tactical positions (`GK`, `DEF`, `MID`, `FWD`).
    - Ⓒ Captain badges.
    - Team-specific match history and upcoming schedule.

### Admin Management Portal

Protected under secure Bearer token authentication (`/admin/login`):

- **📊 Admin Dashboard (`/admin`):**
  - Real-time overview cards for Teams, Players, Matches, and Live Matches.
  - Quick action shortcuts to league operations.
- **🏆 League Configuration (`/admin/league`):**
  - Modify league competition name, season string (e.g. `2025/26`), and status (`active`, `inactive`, `completed`).
- **🛡️ Team Management (`/admin/teams`):**
  - Create new teams with customized club names and logo emojis.
  - Edit team information.
  - Safe team deletion (protected against deleting teams with assigned players or matches).
- **🏃 Roster & Player Management (`/admin/players`):**
  - Register new players with jersey number, squad position, team allocation, and team captain designation.
  - Filter players by team.
  - Update player positions, squad numbers, captain status, or transfer between teams.
  - Remove players from rosters.
- **📅 Match Scheduling (`/admin/matches`):**
  - Schedule fixtures selecting Home Team, Away Team, and Kickoff Date/Time.
  - Filter matches by match status.
- **🎛️ Live Match Control Room (`/admin/matches/:id`):**
  - **Match Lifecycle State Machine:**
    - `Start Match` (`scheduled` → `live`)
    - `Finish Match` (`live` → `finished`)
    - `Cancel Match` (`scheduled` / `live` → `cancelled`)
  - **Live Event Logger:**
    - Log goals in real-time; automatically increments the team's score on the scoreboard.
    - Log yellow cards, red cards, and substitutions with player dropdowns filtered to active match squads.
    - Real-time event removal with automatic score decrement for deleted goal events.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Frontend ["Frontend (React 19 + TypeScript + Vite)"]
        UI[Pages & Components]
        AuthHook[useAuth Context]
        APIClient[API Client: src/api/client.ts]
        TokenStore[(localStorage: scoreboard-token)]
        
        UI --> AuthHook
        UI --> APIClient
        AuthHook --> TokenStore
        APIClient --> TokenStore
    end

    subgraph Backend ["Backend (FastAPI + Python 3.12)"]
        Router[FastAPI Routers: /auth, /league, /teams, /players, /matches, /standings]
        AuthDep[Auth Dependencies & Bearer Verification]
        Store[Database Store Layer: app.store.Database]
        StandingsCalc[Standings Calculation Engine]
        SQLA[SQLAlchemy 2.0 ORM]
        
        Router --> AuthDep
        Router --> Store
        Store --> StandingsCalc
        Store --> SQLA
    end

    subgraph Database ["Database Layer"]
        DB[(SQLite / PostgreSQL / MySQL)]
        SQLA --> DB
    end

    APIClient -- "HTTP / JSON (REST API on :8000)" --> Router
```

---

## 💻 Tech Stack

### Frontend
- **Framework:** [React 19](https://react.dev/)
- **Language:** [TypeScript ~6.0](https://www.typescriptlang.org/)
- **Build Tool & Dev Server:** [Vite 8](https://vitejs.dev/)
- **Routing:** [React Router v7](https://reactrouter.com/)
- **Styling:** Custom Modern Vanilla CSS design system (Dark mode palette, CSS custom properties, glassmorphism cards, responsive flex/grid layouts)
- **Linter:** [Oxlint](https://oxc.rs/) (high-performance Rust-based JavaScript/TypeScript linter)

### Backend
- **Framework:** [FastAPI 0.115+](https://fastapi.tiangolo.com/)
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/) with standard event loop
- **ORM & Database:** [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) (Database-agnostic ORM)
- **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **Authentication & Security:** HTTP Bearer token system with [bcrypt](https://pypi.org/project/bcrypt/) password hashing
- **Testing:** [pytest](https://docs.pytest.org/) with `httpx` and in-memory SQLite isolation

### API Contract & Tooling
- **API Specification:** [OpenAPI 3.0.3](https://swagger.io/specification/) (`openapi.yaml`)
- **Package Managers:** `uv` (Python dependency management) and `npm` (Node.js)
- **Task Runner:** `make` (GNU Makefile for unified developer workflow)

---

## 📁 Repository File Structure

```text
sports-league-scoreboard/
├── Makefile                   # Unified commands (install, dev, test, lint, build, clean)
├── README.md                  # Comprehensive project documentation
├── AGENTS.md                  # Development notes and context
├── openapi.yaml               # Complete OpenAPI 3.0.3 contract specification
│
├── backend/                   # FastAPI backend application
│   ├── pyproject.toml         # Python project configuration & dependencies
│   ├── uv.lock                # Deterministic uv lockfile
│   ├── scoreboard.db          # Default SQLite database file (created on startup)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI entry point, lifespan, CORS, health endpoint
│   │   ├── auth/              # Authentication & authorization module
│   │   │   ├── dependencies.py # FastAPI dependencies: require_auth, get_current_user
│   │   │   ├── password.py    # Bcrypt password hashing and verification
│   │   │   └── tokens.py      # Bearer token generation, storage & validation
│   │   ├── db/                # Database engine & ORM models
│   │   │   ├── base.py        # SQLAlchemy DeclarativeBase definition
│   │   │   ├── engine.py      # Database engine factory (supports SQLite, Postgres, etc.)
│   │   │   ├── init.py        # Table creation & initial seed data script
│   │   │   ├── models.py      # SQLAlchemy ORM models (League, Team, Player, Match, MatchEvent)
│   │   │   └── session.py     # Database session generator dependency
│   │   ├── models/            # Pydantic schemas & enums
│   │   │   └── schemas.py     # Validation schemas for all requests and responses
│   │   ├── routers/           # FastAPI route endpoints
│   │   │   ├── __init__.py    # Central API router aggregating all resource routers
│   │   │   ├── auth.py        # /auth/login, /auth/logout, /auth/me
│   │   │   ├── league.py      # /league GET and PATCH
│   │   │   ├── teams.py       # /teams CRUD endpoints
│   │   │   ├── players.py     # /players CRUD endpoints & team filters
│   │   │   ├── matches.py     # /matches CRUD, state transitions, & event logger
│   │   │   └── standings.py   # /standings calculation endpoint
│   │   └── store/             # Storage repository layer
│   │       ├── database.py    # Database-backed CRUD operations & business logic
│   │       ├── memory.py      # In-memory store reference implementation
│   │       └── standings.py   # Pure function for calculating league standings
│   └── tests/                 # Backend automated test suite (pytest)
│       ├── conftest.py        # Fixtures, test client, and in-memory DB configuration
│       ├── test_auth.py       # Authentication unit & integration tests
│       ├── test_database.py   # Database store persistence tests
│       ├── test_league.py     # League endpoint tests
│       ├── test_matches.py    # Match scheduling, events, scoring & transition tests
│       ├── test_players.py    # Player CRUD & validation tests
│       ├── test_standings.py  # Standings calculation & ranking tests
│       └── test_teams.py      # Team CRUD & deletion constraint tests
│
└── frontend/                  # React 19 + TypeScript SPA
    ├── package.json           # Node.js dependencies & scripts
    ├── package-lock.json      # NPM lockfile
    ├── tsconfig.json          # TypeScript project references
    ├── tsconfig.app.json      # Client application TypeScript configuration
    ├── tsconfig.node.json     # Vite Node TypeScript configuration
    ├── vite.config.ts         # Vite bundler configuration
    ├── .oxlintrc.json         # Oxlint linter rules
    ├── index.html             # HTML entry point
    └── src/
        ├── main.tsx           # React root rendering
        ├── App.tsx            # Route layout & React Router configuration
        ├── index.css          # Design system, tokens, styles & responsive utilities
        ├── api/
        │   ├── client.ts      # HTTP client for backend endpoints with auth header injection
        │   └── mockStore.ts   # Client-side fallback / mock data store
        ├── components/
        │   ├── Layout.tsx     # PublicLayout (header/nav/footer) & AdminLayout (sidebar/nav)
        │   ├── MatchCard.tsx  # Score card component with status badges
        │   ├── StatusBadge.tsx # Visual status indicators (live, finished, scheduled, etc.)
        │   ├── StandingsTable.tsx # Standings table with position, GD, and points
        │   ├── EventTimeline.tsx  # Minute-by-minute match event display
        │   ├── Modal.tsx      # Reusable dialog modal component
        │   └── ProtectedRoute.tsx # Route guard enforcing admin login
        ├── hooks/
        │   ├── useAuth.tsx    # AuthContext provider and useAuth hook
        │   └── useAsyncData.ts # Data fetching hook with loading and error states
        ├── pages/
        │   ├── HomePage.tsx   # Public homepage with standings & recent matches
        │   ├── MatchesPage.tsx # Public fixture schedule & filterable match list
        │   ├── MatchDetailPage.tsx # Public match overview with timeline & score
        │   ├── TeamsPage.tsx  # Public team directory grid
        │   ├── TeamDetailPage.tsx # Public team roster & player details
        │   └── admin/
        │       ├── LoginPage.tsx          # Admin credentials login form
        │       ├── AdminDashboard.tsx      # Admin summary & navigation center
        │       ├── AdminLeaguePage.tsx     # League settings editor
        │       ├── AdminTeamsPage.tsx      # Team creation, editing, & deletion
        │       ├── AdminPlayersPage.tsx    # Player roster registration & transfers
        │       ├── AdminMatchesPage.tsx    # Match scheduler & overview
        │       └── AdminMatchManagePage.tsx # Match control room & live event tracker
        ├── types/
        │   └── index.ts       # Shared TypeScript interfaces & types
        └── utils/
            └── standings.ts   # Frontend standings calculation utilities
```

---

## 🔑 Default Credentials & Seed Data

When started for the first time, the application automatically creates all database tables and seeds them with demo data:

### Admin Login Credentials
- **Email:** `admin@league.com`
- **Password:** `admin123`
- **Login URL:** [http://localhost:5173/admin/login](http://localhost:5173/admin/login)

### Pre-Seeded League & Teams
- **League:** "Premier City League" (Season: `2025/26`, Status: `active`)
- **Teams (4 clubs):**
  1. ⚽ **North United** (`team-1`)
  2. 🦁 **South City FC** (`team-2`)
  3. 🦅 **East Rovers** (`team-3`)
  4. 🐺 **West Athletic** (`team-4`)
- **Players (10 pre-registered):** Squads populated across Goalkeepers, Defenders, Midfielders, and Forwards, with designated captains.
- **Matches (4 pre-scheduled):**
  - 2 finished matches with goal events (North United 2 - 1 South City FC, East Rovers 1 - 1 West Athletic).
  - 2 upcoming scheduled matches.

---

## 🏁 Getting Started

### Prerequisites

Ensure you have the following installed on your system:
- **Python 3.12+** (check with `python --version`)
- **[uv](https://docs.astral.sh/uv/)** (recommended high-speed Python package manager, or standard `pip`)
- **Node.js 18+** and **npm** (check with `node --version` and `npm --version`)
- **make** (standard on Linux/macOS; on Windows available via MinGW, Git Bash, or Chocolatey `choco install make`)

---

### Quickstart (Using Makefile)

The root `Makefile` provides one-liner commands to install and start the entire stack:

```bash
# 1. Clone the repository
git clone https://github.com/combatant936-sketch/sports-league-scoreboard-v1.git
cd sports-league-scoreboard

# 2. Install all backend and frontend dependencies
make install

# 3. Launch both backend and frontend servers in parallel
make dev
```

Once running:
- 🌐 **Frontend Application:** Open [http://localhost:5173](http://localhost:5173) in your browser.
- ⚙️ **Backend API Docs (Swagger UI):** Open [http://localhost:8000/docs](http://localhost:8000/docs).
- 📖 **ReDoc Alternative API Docs:** Open [http://localhost:8000/redoc](http://localhost:8000/redoc).
- 🔐 **Admin Login:** Visit [http://localhost:5173/admin/login](http://localhost:5173/admin/login) and log in with `admin@league.com` / `admin123`.

---

### Manual Setup (Without Makefile)

If you are on Windows PowerShell or prefer running servers in separate terminal tabs:

#### 1. Backend Setup

```bash
cd backend

# Install dependencies using uv
uv sync --all-groups

# Run the FastAPI server with auto-reload on port 8000
uv run uvicorn app.main:app --reload --port 8000
```

*(Alternative with standard pip/venv):*
```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/macOS: source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup

In a new terminal:
```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server on port 5173
npm run dev
```

---

## 🗄️ Database Configuration & Persistence

The backend uses **SQLAlchemy 2.0 ORM** with a database-agnostic repository design. The database connection URL is controlled by the `DATABASE_URL` environment variable:

```bash
# Default (SQLite file on disk)
DATABASE_URL=sqlite:///./scoreboard.db
```

### Supported Databases

| Database | Connection String Format | Notes |
| :--- | :--- | :--- |
| **SQLite (Default)** | `sqlite:///./scoreboard.db` | Zero setup required; stores data in `backend/scoreboard.db`. |
| **SQLite In-Memory** | `sqlite:///:memory:` | Ephemeral in-memory database used by automated pytest suites. |
| **PostgreSQL** | `postgresql+psycopg2://user:password@localhost:5432/scoreboard` | Production ready. Add `psycopg2-binary` or `psycopg` to dependencies. |
| **MySQL / MariaDB** | `mysql+pymysql://user:password@localhost:3306/scoreboard` | Add `pymysql` to dependencies. |

### Automatic Schema Creation & Seeding

The application initializes its database automatically on startup inside FastAPI's `lifespan` context:
1. Calls `Base.metadata.create_all()` to generate tables if they do not yet exist.
2. Checks if the `leagues` table has records.
3. If empty, runs `seed(session)` to populate the initial admin user, teams, players, matches, and match events.
4. If already populated, existing data is preserved untouched.

To reset the database back to clean demo data, simply delete `backend/scoreboard.db` and restart the backend server.

---

## 📊 Database Schema & ER Diagram

```mermaid
erDiagram
    LEAGUES ||--o{ TEAMS : contains
    TEAMS ||--o{ PLAYERS : rosters
    TEAMS ||--o{ MATCHES : "home / away"
    MATCHES ||--o{ MATCH_EVENTS : logs

    LEAGUES {
        string id PK
        string name
        string season
        string status
        string admin_email
        string admin_password_hash
    }

    TEAMS {
        string id PK
        string name
        string logo
        string league_id FK
    }

    PLAYERS {
        string id PK
        string name
        int jersey_number
        string position
        boolean is_captain
        string team_id FK
    }

    MATCHES {
        string id PK
        string home_team_id FK
        string away_team_id FK
        datetime scheduled_at
        string status
        int home_score
        int away_score
    }

    MATCH_EVENTS {
        string id PK
        string match_id FK
        string team_id
        string player_id
        string event_type
        int minute
        string description
        string player_in_id
        string player_out_id
    }
```

---

## ⚖️ Business Logic & Rules

### Match Lifecycle

Matches transition through strict lifecycle states:

```mermaid
stateDiagram-v2
    [*] --> Scheduled: Admin schedules fixture
    Scheduled --> Live: POST /matches/{id}/start
    Scheduled --> Cancelled: POST /matches/{id}/cancel
    Live --> Finished: POST /matches/{id}/finish
    Live --> Cancelled: POST /matches/{id}/cancel
    Finished --> [*]
    Cancelled --> [*]
```

- **`scheduled`:** Fixture is announced. Score remains 0 - 0. Events cannot be logged until match begins.
- **`live`:** Match is actively in progress. Administrators can log goals, bookings, and substitutions.
- **`finished`:** Final whistle blown. The score is locked and counted toward the league standings.
- **`cancelled`:** Match called off. Does not contribute to points or standings.

### Automatic Scoring & Event Handling

When logging match events:
- **Goals (`goal`):**
  - Logging a goal event on a match automatically increments the matching team's score (`home_score` or `away_score`).
  - Deleting a goal event automatically decrements the team's score.
- **Disciplinary Cards (`yellow_card`, `red_card`):**
  - Recorded with the player ID, match minute, and description.
- **Substitutions (`substitution`):**
  - Records both the player entering the pitch (`player_in_id`) and the player leaving (`player_out_id`).

### Standings & Tie-Breaking Calculation

Standings are computed dynamically on demand from all `finished` matches according to standard association football rules:
- **Points Awarded:**
  - **Win:** 3 points
  - **Draw:** 1 point
  - **Loss:** 0 points
- **Ranking / Tie-Breaking Hierarchy:**
  1. **Points (`PTS`):** Highest total points first.
  2. **Goal Difference (`GD`):** $\text{Goals For} - \text{Goals Against}$.
  3. **Goals For (`GF`):** Highest total goals scored.
  4. **Team Name:** Alphabetical ascending order.

---

## 🔌 REST API Reference & OpenAPI Specification

The backend adheres strictly to the OpenAPI 3.0.3 specification documented in [`openapi.yaml`](openapi.yaml).

Interactive documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Authentication

| Endpoint | Method | Security | Description |
| :--- | :---: | :---: | :--- |
| `/auth/login` | `POST` | Public | Authenticate with `{ email, password }` and obtain a Bearer token. |
| `/auth/logout` | `POST` | Bearer | Revoke the current Bearer token. |
| `/auth/me` | `GET` | Optional Bearer | Returns `{ email }` of the authenticated admin, or `null` if unauthenticated. |

### League Settings

| Endpoint | Method | Security | Description |
| :--- | :---: | :---: | :--- |
| `/league` | `GET` | Public | Retrieve current league details (id, name, season, status). |
| `/league` | `PATCH` | Bearer | Update league information (name, season, status: `active` \| `inactive` \| `completed`). |

### Teams

| Endpoint | Method | Security | Description |
| :--- | :---: | :---: | :--- |
| `/teams` | `GET` | Public | List all teams registered in the league. |
| `/teams` | `POST` | Bearer | Register a new team with `{ name, logo }`. |
| `/teams/{id}` | `GET` | Public | Retrieve details for a specific team. |
| `/teams/{id}` | `PATCH` | Bearer | Update team name or logo. |
| `/teams/{id}` | `DELETE` | Bearer | Delete a team (rejected if team has assigned players or matches). |

### Players

| Endpoint | Method | Security | Description |
| :--- | :---: | :---: | :--- |
| `/players` | `GET` | Public | List all players (supports optional query filter `?teamId={id}`). |
| `/players` | `POST` | Bearer | Create a player `{ name, jerseyNumber, position, isCaptain, teamId }`. |
| `/players/{id}` | `GET` | Public | Retrieve details for a specific player. |
| `/players/{id}` | `PATCH` | Bearer | Update player name, number, position, captain flag, or team assignment. |
| `/players/{id}` | `DELETE` | Bearer | Remove a player from the league. |

### Matches & Scheduling

| Endpoint | Method | Security | Description |
| :--- | :---: | :---: | :--- |
| `/matches` | `GET` | Public | List matches (supports optional query filter `?status={status}`). |
| `/matches` | `POST` | Bearer | Schedule a new match with `{ homeTeamId, awayTeamId, scheduledAt }`. |
| `/matches/{id}` | `GET` | Public | Retrieve match details and current score. |
| `/matches/{id}` | `PATCH` | Bearer | Reschedule match or change teams. |
| `/matches/{id}/start` | `POST` | Bearer | Transition match status from `scheduled` to `live`. |
| `/matches/{id}/finish` | `POST` | Bearer | Transition match status from `live` to `finished`. |
| `/matches/{id}/cancel` | `POST` | Bearer | Cancel a scheduled or live match. |

### Match Events & Live Scoreboard

| Endpoint | Method | Security | Description |
| :--- | :---: | :---: | :--- |
| `/matches/{id}/events` | `GET` | Public | Retrieve all recorded events for a match sorted chronologically. |
| `/matches/{id}/events` | `POST` | Bearer | Add an event (`goal`, `yellow_card`, `red_card`, `substitution`). Automatically updates score for goals. |
| `/matches/{matchId}/events/{eventId}` | `DELETE` | Bearer | Delete a recorded event. Automatically adjusts score if a goal is removed. |

### Standings & System Health

| Endpoint | Method | Security | Description |
| :--- | :---: | :---: | :--- |
| `/standings` | `GET` | Public | Computes and returns the sorted league table. |
| `/health` | `GET` | Public | Returns `{"status": "ok"}` for container/liveness checks. |

---

## 🧪 Testing & Quality Assurance

The project includes automated backend testing, frontend linting, and typecheck builds:

### Running Backend Unit & Integration Tests

Backend tests run against an isolated in-memory SQLite database (`sqlite:///:memory:`) using `pytest` and `fastapi.testclient.TestClient`:

```bash
# Run tests with make
make test

# Or run directly inside the backend directory
cd backend
uv run pytest -v
```

**Test coverage spans 39 tests across:**
- `test_auth.py`: Token generation, invalid passwords, logout revocation, protected endpoint guards.
- `test_database.py`: SQLAlchemy store persistence, table isolation, CRUD operations.
- `test_league.py`: League retrieval, partial updates.
- `test_teams.py`: Team registration, duplicate names, relational deletion integrity.
- `test_players.py`: Squad numbers, positional enums, captain toggles, team assignment filters.
- `test_matches.py`: Status machine transitions (`start`, `finish`, `cancel`), event logging, automatic score synchronization.
- `test_standings.py`: Multi-team standings calculation, tie-breaking on goal difference and goals scored.

### Running Frontend Linter & Build Validation

```bash
# Lint frontend TypeScript and React code using Oxlint
make lint

# Or directly in the frontend directory
cd frontend
npm run lint

# Validate TypeScript types and build production bundle
make build
# (or cd frontend && npm run build)
```

---

## 🛠️ Makefile Command Reference

Run `make help` to inspect all available targets:

| Command | Action | Description |
| :--- | :--- | :--- |
| `make help` | Show help | Displays formatted list of available targets with descriptions. |
| `make install` | Install All | Installs both backend (`uv sync --all-groups`) and frontend (`npm install`). |
| `make install-backend` | Install Backend | Installs Python packages using `uv`. |
| `make install-frontend` | Install Frontend | Installs Node packages using `npm`. |
| `make dev` | Run Dev Servers | Concurrently runs backend (:8000) and frontend (:5173). |
| `make dev-backend` | Run Backend | Runs FastAPI with Uvicorn and hot-reload. |
| `make dev-frontend` | Run Frontend | Runs Vite development server. |
| `make test` | Run Tests | Executes the backend `pytest` test suite. |
| `make lint` | Run Linter | Lints the frontend code using `oxlint`. |
| `make build` | Build Production | Compiles TypeScript and builds production distribution (`frontend/dist`). |
| `make clean` | Clean Artifacts | Removes `frontend/dist`, `__pycache__`, and `*.pyc` files. |

---

## ❓ Troubleshooting & FAQ

### 1. Port Conflicts (8000 or 5173 already in use)
- **Backend (Port 8000):** If port 8000 is occupied, you can run uvicorn on another port:
  ```bash
  cd backend
  uv run uvicorn app.main:app --reload --port 8080
  ```
  *(Note: Update `BASE_URL` in `frontend/src/api/client.ts` to point to the new port).*
- **Frontend (Port 5173):** Vite will automatically select the next available port (e.g. 5174).

### 2. How to Reset the Database to Fresh Demo Data
If test data accumulated or you want to return to a clean slate:
```bash
# Stop dev servers, then remove the SQLite database file:
rm backend/scoreboard.db

# Restart the backend. Tables and initial seed data will be recreated automatically.
```

### 3. How to Connect to PostgreSQL Instead of SQLite
1. Install a Postgres driver in the backend (e.g., `uv add psycopg2-binary` or `pip install psycopg2-binary`).
2. Set the `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql+psycopg2://postgres:password@localhost:5432/sports_league"
   ```
3. Restart the backend server. Tables and seed data will be generated in PostgreSQL automatically.

### 4. CORS Errors in the Browser
CORS is pre-configured in `backend/app/main.py` for `http://localhost:5173` and `http://127.0.0.1:5173`. If you access the frontend using a custom host or port, add your origin to the `allow_origins` list in `backend/app/main.py`.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
