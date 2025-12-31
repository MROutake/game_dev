"""
Spotify Playlist Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..services.spotify_service import spotify_service
from ..models.game import PlaylistInfo, SpotifyTrack

router = APIRouter(prefix="/playlist", tags=["Playlist"])


@router.get("/{playlist_id}", response_model=PlaylistInfo)
async def get_playlist(playlist_id: str):
    """
    Hole Playlist Informationen & Tracks
    """
    try:
        playlist_info = spotify_service.get_playlist_tracks(playlist_id)
        return playlist_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Playlist nicht gefunden: {str(e)}")


@router.get("/track/{track_id}", response_model=SpotifyTrack)
async def get_track(track_id: str):
    """
    Hole einzelnen Track
    """
    try:
        track = spotify_service.get_track_info(track_id)
        return track
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Track nicht gefunden: {str(e)}")


@router.get("/search/tracks", response_model=List[SpotifyTrack])
async def search_tracks(query: str, limit: int = 20):
    """
    Suche nach Tracks
    """
    try:
        tracks = spotify_service.search_tracks(query, limit)
        return tracks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search Error: {str(e)}")
