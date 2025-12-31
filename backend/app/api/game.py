"""
Game Endpoints - Session, Players, Gameplay
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.game_service import game_service
from ..services.websocket_service import broadcast_to_session
from ..models.game import (
    GameSession, 
    Player, 
    GuessRequest, 
    GuessResult,
    PlacementRequest,
    PlacementResult,
    TimelineCard,
    GameMode,
    TokenActionRequest,
    TokenActionResult
)

router = APIRouter(prefix="/game", tags=["Game"])


class CreateSessionRequest(BaseModel):
    host_name: str
    playlist_id: Optional[str] = None
    game_mode: Optional[GameMode] = GameMode.ORIGINAL


class AddPlayerRequest(BaseModel):
    session_id: str
    player_name: str


class LoadPlaylistRequest(BaseModel):
    session_id: str
    playlist_id: str


class NextTrackRequest(BaseModel):
    session_id: str


@router.post("/session/create", response_model=GameSession)
async def create_session(request: CreateSessionRequest):
    """
    Erstelle neue Game Session
    """
    try:
        session = game_service.create_session(
            host_name=request.host_name,
            playlist_id=request.playlist_id,
            game_mode=request.game_mode or GameMode.ORIGINAL
        )
        
        # Hole den Host-Spieler
        host_player = game_service.players.get(session.session_id, [])[0] if game_service.players.get(session.session_id) else None
        
        # Füge host_player_id zur Response hinzu
        response = session.model_dump()
        if host_player:
            response['host_player_id'] = host_player.player_id
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/player/add", response_model=Player)
async def add_player(request: AddPlayerRequest):
    """
    Füge Spieler zur Session hinzu
    """
    try:
        player = game_service.add_player(
            session_id=request.session_id,
            player_name=request.player_name
        )
        
        # WebSocket: Benachrichtige alle in der Lobby
        await broadcast_to_session(request.session_id, 'player_joined', {
            'player_id': player.player_id,
            'name': player.name,
            'score': player.score
        })
        
        return player
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/playlist/load")
async def load_playlist(request: LoadPlaylistRequest):
    """
    Lade Playlist in Session
    """
    try:
        track_count = game_service.load_playlist(
            session_id=request.session_id,
            playlist_id=request.playlist_id
        )
        return {
            "message": "Playlist geladen",
            "track_count": track_count
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_game(session_id: str):
    """
    Starte das Spiel
    """
    try:
        result = game_service.start_game(session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-track/{session_id}")
async def get_current_track(session_id: str):
    """
    Hole aktuellen Track (für Playback, ohne Lösung)
    """
    try:
        track_info = game_service.get_current_track_for_playback(session_id)
        return track_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guess", response_model=GuessResult)
async def submit_guess(guess: GuessRequest):
    """
    Sende Guess & erhalte Ergebnis
    """
    try:
        result = game_service.check_guess(guess)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/next")
async def next_track(request: NextTrackRequest):
    """
    Gehe zum nächsten Track
    """
    try:
        result = game_service.next_track(request.session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard/{session_id}")
async def get_leaderboard(session_id: str) -> List[Dict]:
    """
    Hole Leaderboard für Session
    """
    try:
        leaderboard = game_service.get_leaderboard(session_id)
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# TIMELINE-ENDPOINTS (HITSTER Original)
# =====================================================

@router.post("/place-card", response_model=PlacementResult)
async def place_card(placement: PlacementRequest):
    """
    Platziere Karte in Timeline (Hauptmechanik)
    """
    try:
        result = game_service.place_card_in_timeline(placement)
        
        # WebSocket: Benachrichtige alle über Platzierung
        await broadcast_to_session(placement.session_id, 'card_placed', {
            'player_id': placement.player_id,
            'correct': result.correct,
            'new_score': result.new_score,
            'won_game': result.won_game,
            'earned_token': result.earned_token
        })
        
        if result.won_game:
            await broadcast_to_session(placement.session_id, 'game_won', {
                'player_id': placement.player_id,
                'final_score': result.new_score
            })
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/{session_id}/{player_id}")
async def get_timeline(session_id: str, player_id: str) -> List[TimelineCard]:
    """
    Hole Timeline eines Spielers
    """
    try:
        timeline = game_service.get_player_timeline(session_id, player_id)
        return timeline
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# TOKEN-SYSTEM ENDPOINTS
# =====================================================

@router.post("/token-action", response_model=TokenActionResult)
async def use_token_action(action: TokenActionRequest):
    """
    Führe Token-Aktion aus (Skip Song, Steal Card, Buy Card)
    """
    try:
        result = game_service.use_token_action(action)
        
        # WebSocket: Benachrichtige alle über Token-Aktion
        await broadcast_to_session(action.session_id, 'token_action_used', {
            'player_id': action.player_id,
            'action_type': action.action_type.value,
            'success': result.success,
            'message': result.message,
            'new_token_count': result.new_token_count
        })
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
