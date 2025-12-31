"""
Data Models für Game & Spotify
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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


class GameSession(BaseModel):
    """Game Session"""
    session_id: str
    host_name: str
    playlist_id: Optional[str] = None
    current_track_index: int = 0
    started_at: Optional[datetime] = None
    status: str = "waiting"  # waiting, playing, finished


class Player(BaseModel):
    """Player in Session"""
    player_id: str
    name: str
    score: int = 0
    session_id: str


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
