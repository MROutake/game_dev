"""
WebSocket Service für Live-Updates
"""
import socketio
from typing import Dict, Set

# Socket.IO Server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Track connected clients per session
connected_clients: Dict[str, Set[str]] = {}  # session_id -> set of sid
# Track player_id to session mapping
player_sessions: Dict[str, str] = {}  # sid -> session_id
player_ids: Dict[str, str] = {}  # sid -> player_id


@sio.event
async def connect(sid, environ):
    """Client verbindet sich"""
    print(f"✅ Client connected: {sid}")


@sio.event
async def disconnect(sid):
    """Client trennt Verbindung"""
    print(f"❌ Client disconnected: {sid}")
    
    # Hole Session und Player ID
    session_id = player_sessions.pop(sid, None)
    player_id = player_ids.pop(sid, None)
    
    if session_id:
        # Entferne aus Session
        if session_id in connected_clients:
            connected_clients[session_id].discard(sid)
        
        # Entferne Spieler aus Game Service
        if player_id:
            from .game_service import game_service
            was_host = False
            
            # Prüfe ob es der Host war (erster Spieler)
            if session_id in game_service.players:
                players = game_service.players[session_id]
                if len(players) > 0 and players[0].player_id == player_id:
                    was_host = True
                    print(f"👑 Host verlässt Session {session_id}")
            
            game_service.remove_player(session_id, player_id)
            
            # Informiere andere
            await sio.emit('player_left', {
                'player_id': player_id,
                'was_host': was_host
            }, room=session_id)
            
            # Wenn Host, schließe Session
            if was_host:
                await sio.emit('session_closed', {
                    'message': 'Host hat die Lobby verlassen'
                }, room=session_id)
                # Räume auf
                if session_id in connected_clients:
                    del connected_clients[session_id]


@sio.event
async def join_lobby(sid, data):
    """Client tritt Lobby bei"""
    session_id = data.get('session_id')
    player_name = data.get('player_name', 'Spieler')
    player_id = data.get('player_id')
    
    print(f"👤 {player_name} (sid={sid}) tritt Lobby {session_id} bei")
    
    # Speichere Zuordnung
    player_sessions[sid] = session_id
    if player_id:
        player_ids[sid] = player_id
    
    # Füge zur Session hinzu
    if session_id not in connected_clients:
        connected_clients[session_id] = set()
    connected_clients[session_id].add(sid)
    
    # Socket.IO Room beitreten
    await sio.enter_room(sid, session_id)
    
    # Informiere alle anderen in der Lobby
    await sio.emit('player_joined', {
        'player_id': player_id,
        'player_name': player_name,
        'sid': sid
    }, room=session_id, skip_sid=sid)
    
    # Sende Bestätigung an den Client
    await sio.emit('joined_lobby', {
        'session_id': session_id,
        'message': 'Erfolgreich beigetreten'
    }, to=sid)


@sio.event
async def start_game(sid, data):
    """Host startet das Spiel"""
    session_id = data.get('session_id')
    print(f"🎮 Spiel startet in Session {session_id}")
    
    # Setze Status auf "playing"
    from .game_service import game_service
    if session_id in game_service.sessions:
        game_service.sessions[session_id].status = "playing"
        print(f"✅ Session {session_id} Status → playing")
    
    # Alle in der Session informieren
    await sio.emit('game_started', {
        'session_id': session_id,
        'message': 'Spiel wurde gestartet!'
    }, room=session_id)


@sio.event
async def guess_submitted(sid, data):
    """Spieler hat geraten"""
    session_id = data.get('session_id')
    
    # An alle in der Session senden
    await sio.emit('guess_result', data, room=session_id)


@sio.event
async def next_track_request(sid, data):
    """Host fordert nächsten Track an"""
    session_id = data.get('session_id')
    
    # An alle in der Session senden
    await sio.emit('new_track', data, room=session_id)


async def broadcast_to_session(session_id: str, event: str, data: dict):
    """Helper: Sende Event an alle in einer Session"""
    await sio.emit(event, data, room=session_id)


async def send_to_client(sid: str, event: str, data: dict):
    """Helper: Sende Event an spezifischen Client"""
    await sio.emit(event, data, to=sid)
