# Football League Scoreboard — Implementation Specification

## 1. Authentication

* Admin login with email and password.
* Only authenticated admins can modify league data.
* Public users do not require authentication.

## 2. League

* Create and manage one football league.
* League fields:

  * ID
  * Name
  * Season
  * Status

## 3. Teams

Admin can:

* Create team
* Update team
* Delete team
* View team

Team fields:

* ID
* Name
* Logo
* League ID

## 4. Players

Admin can:

* Create player
* Update player
* Delete player
* Assign player to a team

Player fields:

* ID
* Name
* Jersey number
* Position
* Captain status
* Team ID

## 5. Matches

Admin can:

* Create match
* Update scheduled match
* Start match
* Cancel match
* Finish match
* View match

Match fields:

* ID
* Home team
* Away team
* Scheduled date/time
* Status
* Home score
* Away score

Match statuses:

* Scheduled
* Live
* Finished
* Cancelled

## 6. Match Events

Admin can add and remove events during a match.

Supported events:

* Goal
* Yellow card
* Red card
* Substitution

Event fields:

* ID
* Match ID
* Team ID
* Player ID
* Event type
* Minute
* Description

Substitution additionally stores:

* Player coming in
* Player going out

## 7. Automatic Score

* A goal event increases the corresponding team's score.
* Match score is calculated from goal events.
* Finished match score is used for league standings.

## 8. League Standings

Automatically calculate:

* Position
* Team
* Played
* Wins
* Draws
* Losses
* Goals For
* Goals Against
* Goal Difference
* Points

Scoring:

* Win = 3 points
* Draw = 1 point
* Loss = 0 points

Ranking order:

1. Points
2. Goal Difference
3. Goals For

## 9. Public Views

Public users can view:

### League

* League information
* Current standings

### Teams

* Team list
* Team details
* Players

### Matches

* Upcoming matches
* Live matches
* Finished matches
* Match score
* Match events/timeline

## 10. Required API Areas

```text
/auth
/league
/teams
/players
/matches
/matches/{id}/events
/standings
```

The implementation must include **authentication, CRUD operations, database relationships, match state management, event recording, automatic scoring, and automatic standings calculation**.
