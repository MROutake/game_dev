"""
Lobby Discovery & Management Endpoints
Für lokales Netzwerk Discovery
"""
from fastapi import APIRouter
from typing import List, Dict
from ..services.game_service import game_service
from ..models.game import GameSession

router = APIRouter(prefix="/game", tags=["Lobby"])


@router.get("/lobbies")
async def get_lobbies() -> List[Dict]:
    """
    Hole alle verfügbaren Lobbys (für Discovery)
    Zeigt nur Lobbies mit Status "waiting"
    """
    print(f"🔍 GET /lobbies - Verfügbare Sessions: {len(game_service.sessions)}")
    lobbies = []
    
    for session_id, session in game_service.sessions.items():
        # Zeige nur wartende Lobbys (nicht "playing" oder "finished")
        if session.status != "waiting":
            print(f"   ⏭️ Überspringe Lobby {session.session_id} (Status: {session.status})")
            continue
            
        player_count = len(game_service.players.get(session_id, []))
        
        lobby_info = {
            "session_id": session.session_id,
            "host_name": session.host_name,
            "player_count": player_count,
            "status": session.status,
            "created_at": session.started_at.isoformat() if session.started_at else None
        }
        print(f"   ✅ Lobby beitretbar: {lobby_info}")
        lobbies.append(lobby_info)
    
    print(f"📤 Sende {len(lobbies)} beitretbare Lobbies zurück")
    return lobbies


@router.get("/session/{session_id}/players")
async def get_session_players(session_id: str):
    """
    Hole alle Spieler einer Session
    """
    if session_id not in game_service.sessions:
        return {"error": "Session nicht gefunden"}
    
    players = game_service.players.get(session_id, [])
    
    return {
        "session_id": session_id,
        "players": [
            {
                "player_id": p.player_id,
                "name": p.name,
                "score": p.score
            }
            for p in players
        ]
    }


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Hole Session-Status
    """
    if session_id not in game_service.sessions:
        return {"error": "Session nicht gefunden"}
    
    session = game_service.sessions[session_id]
    player_count = len(game_service.players.get(session_id, []))
    
    return {
        "session_id": session.session_id,
        "host_name": session.host_name,
        "status": session.status,
        "player_count": player_count,
        "current_track_index": session.current_track_index
    }
