"""
Spotify API Service - Integration mit Spotipy
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from typing import List, Optional, Dict, Any
import random
from ..core.config import settings
from ..models.game import SpotifyTrack, PlaylistInfo


class SpotifyService:
    """
    Spotify API Service
    Handles authentication, playlist management, and track metadata
    """
    
    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.redirect_uri = settings.spotify_redirect_uri
        self.scope = "user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative"
        
        # Client Credentials für öffentliche Daten
        self.client = None
        # OAuth für User-spezifische Aktionen
        self.oauth = None
        self.user_client = None
    
    def get_auth_url(self) -> str:
        """
        Generiere Spotify Authorization URL für OAuth Flow
        """
        self.oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=".spotify_cache"
        )
        return self.oauth.get_authorize_url()
    
    def authenticate_with_code(self, code: str) -> Dict[str, Any]:
        """
        Authentifiziere mit Authorization Code
        Returns: Token Info
        """
        if not self.oauth:
            self.oauth = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
        
        token_info = self.oauth.get_access_token(code)
        self.user_client = spotipy.Spotify(auth=token_info['access_token'])
        return token_info
    
    def set_user_token(self, access_token: str):
        """
        Setze User Access Token für authentifizierte Requests
        """
        self.user_client = spotipy.Spotify(auth=access_token)
    
    def get_playlist_tracks(self, playlist_id: str) -> PlaylistInfo:
        """
        Hole alle Tracks aus einer Playlist
        """
        if not self.user_client:
            # Fallback auf Client Credentials
            if not self.client:
                self.client = spotipy.Spotify(
                    client_credentials_manager=SpotifyClientCredentials(
                        client_id=self.client_id,
                        client_secret=self.client_secret
                    )
                )
            sp = self.client
        else:
            sp = self.user_client
        
        # Playlist Info
        playlist = sp.playlist(playlist_id)
        
        # Alle Tracks holen (Pagination beachten)
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        
        while results:
            for item in results['items']:
                if item['track']:  # Manchmal sind Tracks None
                    track = self._parse_track(item['track'])
                    tracks.append(track)
            
            # Nächste Page
            if results['next']:
                results = sp.next(results)
            else:
                results = None
        
        return PlaylistInfo(
            playlist_id=playlist_id,
            name=playlist['name'],
            owner=playlist['owner']['display_name'],
            total_tracks=len(tracks),
            tracks=tracks
        )
    
    def get_track_info(self, track_id: str) -> SpotifyTrack:
        """
        Hole Metadaten für einen einzelnen Track
        """
        sp = self.user_client or self._get_client()
        track_data = sp.track(track_id)
        return self._parse_track(track_data)
    
    def shuffle_tracks(self, tracks: List[SpotifyTrack]) -> List[SpotifyTrack]:
        """
        Mische Tracks zufällig
        """
        shuffled = tracks.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def _parse_track(self, track_data: Dict) -> SpotifyTrack:
        """
        Parse Spotify Track Data zu SpotifyTrack Model
        """
        # Artists als String zusammenfügen
        artists = ", ".join([artist['name'] for artist in track_data['artists']])
        
        # Release Date & Decade
        release_date = track_data['album']['release_date']
        decade = self._get_decade(release_date)
        
        return SpotifyTrack(
            track_id=track_data['id'],
            title=track_data['name'],
            artist=artists,
            album=track_data['album']['name'],
            release_date=release_date,
            decade=decade,
            duration_ms=track_data['duration_ms'],
            preview_url=track_data.get('preview_url'),
            uri=track_data['uri']
        )
    
    def _get_decade(self, release_date: str) -> str:
        """
        Berechne Jahrzehnt aus Release Date
        z.B. '1994-08-23' -> '1990er'
        """
        try:
            year = int(release_date[:4])
            decade_start = (year // 10) * 10
            return f"{decade_start}er"
        except (ValueError, IndexError):
            return "Unbekannt"
    
    def _get_client(self):
        """
        Get or create basic client
        """
        if not self.client:
            self.client = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            )
        return self.client
    
    def search_tracks(self, query: str, limit: int = 20) -> List[SpotifyTrack]:
        """
        Suche nach Tracks (für spätere Features)
        """
        sp = self.user_client or self._get_client()
        results = sp.search(q=query, type='track', limit=limit)
        
        tracks = []
        for item in results['tracks']['items']:
            track = self._parse_track(item)
            tracks.append(track)
        
        return tracks


# Singleton Instance
spotify_service = SpotifyService()
