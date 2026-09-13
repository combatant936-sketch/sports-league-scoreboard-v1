from fastapi import APIRouter

from app.routers import auth, league, matches, players, standings, teams

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(league.router)
api_router.include_router(teams.router)
api_router.include_router(players.router)
api_router.include_router(matches.router)
api_router.include_router(standings.router)
