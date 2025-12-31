"""
Data Models für Game & Spotify
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GameMode(str, Enum):
    """Spielmodi"""
    ORIGINAL = "original"  # Nur Timeline-Platzierung
    PRO = "pro"           # Timeline + Titel + Künstler
    EXPERT = "expert"     # Timeline + Titel + Künstler + Jahr
    TEAMWORK = "teamwork" # Kooperativ


class SpotifyTrack(BaseModel):
    """Spotify Track Metadata"""
    track_id: str
    title: str
    artist: str
    album: str
    release_date: str
    decade: str
    duration_ms: int
    preview_url: Optional[str] = None
    uri: str


class TimelineCard(BaseModel):
    """Karte in der Timeline eines Spielers"""
    position: int  # Position in der Timeline (0 = älteste)
    track_id: str
    title: str
    artist: str
    year: int  # Nur das Jahr
    is_correct: bool = True  # Wurde richtig platziert?


class GameSession(BaseModel):
    """Game Session"""
    session_id: str
    host_name: str
    playlist_id: Optional[str] = None
    current_track_index: int = 0
    started_at: Optional[datetime] = None
    status: str = "waiting"  # waiting, playing, finished
    
    # NEU: HITSTER-Mechaniken
    game_mode: GameMode = GameMode.ORIGINAL
    win_condition: int = 10  # Anzahl Karten zum Gewinnen
    current_player_turn: Optional[str] = None  # player_id des Spielers am Zug
    round_number: int = 0


class Player(BaseModel):
    """Player in Session"""
    player_id: str
    name: str
    score: int = 0  # Anzahl richtig platzierter Karten
    session_id: str
    
    # NEU: HITSTER-Token & Timeline
    tokens: int = 2  # HITSTER-Token (2 bei ORIGINAL, 5 bei PRO, 3 bei EXPERT)
    timeline: List[TimelineCard] = []  # Eigene Zeitleiste
    has_won: bool = False


class PlacementRequest(BaseModel):
    """Request zum Platzieren einer Karte in der Timeline"""
    session_id: str
    player_id: str
    position: int  # Wo soll die Karte platziert werden? (Index in Timeline)
    
    # Optional: Titel/Künstler-Guess für Token (PRO/EXPERT)
    title_guess: Optional[str] = None
    artist_guess: Optional[str] = None
    year_guess: Optional[int] = None  # Nur bei EXPERT


class PlacementResult(BaseModel):
    """Ergebnis einer Kartenplatzierung"""
    correct: bool
    won_game: bool = False
    new_score: int
    earned_token: bool = False  # Token durch richtigen Titel+Künstler
    correct_year: int
    correct_title: str
    correct_artist: str
    player_timeline: List[TimelineCard] = []


class GuessRequest(BaseModel):
    """Player's Guess"""
    session_id: str
    player_id: str
    title_guess: Optional[str] = None
    artist_guess: Optional[str] = None
    decade_guess: Optional[str] = None


class GuessResult(BaseModel):
    """Result of a Guess"""
    correct_title: bool
    correct_artist: bool
    correct_decade: bool
    points_earned: int
    total_score: int
    correct_answers: dict


class PlaylistInfo(BaseModel):
    """Playlist Information"""
    playlist_id: str
    name: str
    owner: str
    total_tracks: int
    tracks: List[SpotifyTrack] = []


# =====================================================
# TOKEN-SYSTEM (HITSTER Actions)
# =====================================================

class TokenActionType(str, Enum):
    """Token-Aktionstypen"""
    SKIP_SONG = "skip_song"      # 1 Token: Song überspringen
    STEAL_CARD = "steal_card"    # 1 Token: Karte stehlen (+ Guess)
    BUY_CARD = "buy_card"        # 3 Token: Karte kaufen (automatisch korrekt)


class TokenActionRequest(BaseModel):
    """Request für Token-Aktion"""
    action_type: TokenActionType
    session_id: str
    player_id: str
    
    # Für STEAL_CARD:
    target_player_id: Optional[str] = None
    target_position: Optional[int] = None  # Welche Karte stehlen?
    title_guess: Optional[str] = None
    artist_guess: Optional[str] = None
    year_guess: Optional[int] = None  # Nur bei EXPERT


class TokenActionResult(BaseModel):
    """Ergebnis einer Token-Aktion"""
    success: bool
    tokens_spent: int
    new_token_count: int
    message: str
    stolen_card: Optional[TimelineCard] = None  # Bei erfolgreichem Diebstahl
