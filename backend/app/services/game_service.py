"""
Game Service - Spiel-Logik & Session Management
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from ..models.game import (
    GameSession,
    Player,
    SpotifyTrack,
    GuessRequest,
    GuessResult
)
from .spotify_service import spotify_service


class GameService:
    """
    Game Service
    Verwaltet Sessions, Spieler, Scores und Spiel-Logik
    """
    
    def __init__(self):
        # In-Memory Storage (später durch DB ersetzen)
        self.sessions: Dict[str, GameSession] = {}
        self.players: Dict[str, List[Player]] = {}  # session_id -> [players]
        self.track_queues: Dict[str, List[SpotifyTrack]] = {}  # session_id -> [tracks]
        self.solutions: Dict[str, SpotifyTrack] = {}  # session_id -> current_track
    
    def create_session(self, host_name: str, playlist_id: Optional[str] = None) -> GameSession:
        """
        Erstelle neue Game Session
        """
        session_id = str(uuid.uuid4())
        
        session = GameSession(
            session_id=session_id,
            host_name=host_name,
            playlist_id=playlist_id,
            current_track_index=0,
            status="waiting"
        )
        
        self.sessions[session_id] = session
        self.players[session_id] = []
        
        # Host automatisch als ersten Spieler hinzufügen
        host_player = Player(
            player_id=str(uuid.uuid4()),
            name=host_name,
            score=0,
            session_id=session_id
        )
        self.players[session_id].append(host_player)
        
        return session
    
    def add_player(self, session_id: str, player_name: str) -> Player:
        """
        Füge Spieler zur Session hinzu
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} nicht gefunden")
        
        player_id = str(uuid.uuid4())
        player = Player(
            player_id=player_id,
            name=player_name,
            score=0,
            session_id=session_id
        )
        
        self.players[session_id].append(player)
        return player
    
    def remove_player(self, session_id: str, player_id: str) -> bool:
        """
        Entferne Spieler aus Session
        Returns: True wenn Spieler entfernt wurde
        """
        if session_id not in self.players:
            return False
        
        initial_count = len(self.players[session_id])
        self.players[session_id] = [
            p for p in self.players[session_id] 
            if p.player_id != player_id
        ]
        
        removed = len(self.players[session_id]) < initial_count
        
        if removed:
            print(f"🚪 Spieler {player_id} aus Session {session_id} entfernt")
            # Prüfe ob Host entfernt wurde (erster Spieler)
            if initial_count > 0 and len(self.players[session_id]) == 0:
                print(f"⚠️ Letzter Spieler verlassen - lösche Session")
                self.delete_session(session_id)
        
        return removed
    
    def delete_session(self, session_id: str) -> bool:
        """
        Lösche Session komplett
        """
        if session_id not in self.sessions:
            return False
        
        # Cleanup
        self.sessions.pop(session_id, None)
        self.players.pop(session_id, None)
        self.track_queues.pop(session_id, None)
        self.solutions.pop(session_id, None)
        
        print(f"🗑️ Session {session_id} gelöscht")
        return True
    
    def load_playlist(self, session_id: str, playlist_id: str) -> int:
        """
        Lade Playlist und mische Tracks
        Returns: Anzahl der Tracks
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} nicht gefunden")
        
        # Playlist von Spotify laden
        playlist_info = spotify_service.get_playlist_tracks(playlist_id)
        
        # Tracks mischen
        shuffled_tracks = spotify_service.shuffle_tracks(playlist_info.tracks)
        
        # Speichern
        self.track_queues[session_id] = shuffled_tracks
        self.sessions[session_id].playlist_id = playlist_id
        
        return len(shuffled_tracks)
    
    def start_game(self, session_id: str) -> Dict:
        """
        Starte das Spiel
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} nicht gefunden")
        
        if session_id not in self.track_queues or len(self.track_queues[session_id]) == 0:
            raise ValueError("Keine Tracks in der Queue. Lade zuerst eine Playlist.")
        
        session = self.sessions[session_id]
        session.status = "playing"
        session.started_at = datetime.now()
        session.current_track_index = 0
        
        # Ersten Track laden
        current_track = self.track_queues[session_id][0]
        self.solutions[session_id] = current_track
        
        return {
            "session_id": session_id,
            "status": "playing",
            "total_tracks": len(self.track_queues[session_id]),
            "current_track": {
                "track_id": current_track.track_id,
                "uri": current_track.uri,
                "duration_ms": current_track.duration_ms
                # KEINE Lösung senden!
            }
        }
    
    def get_current_track_for_playback(self, session_id: str) -> Dict:
        """
        Hole aktuellen Track für Playback (ohne Lösung)
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} nicht gefunden")
        
        session = self.sessions[session_id]
        tracks = self.track_queues.get(session_id, [])
        
        if session.current_track_index >= len(tracks):
            return {"status": "finished", "message": "Alle Songs gespielt!"}
        
        current_track = tracks[session.current_track_index]
        
        return {
            "track_id": current_track.track_id,
            "uri": current_track.uri,
            "duration_ms": current_track.duration_ms,
            "track_number": session.current_track_index + 1,
            "total_tracks": len(tracks)
        }
    
    def check_guess(self, guess: GuessRequest) -> GuessResult:
        """
        Überprüfe Spieler-Guess und berechne Punkte
        """
        session_id = guess.session_id
        
        if session_id not in self.solutions:
            raise ValueError("Kein aktiver Track für diese Session")
        
        solution = self.solutions[session_id]
        
        # Vergleiche (case-insensitive, stripped)
        correct_title = False
        correct_artist = False
        correct_decade = False
        
        if guess.title_guess:
            correct_title = self._fuzzy_match(guess.title_guess, solution.title)
        
        if guess.artist_guess:
            correct_artist = self._fuzzy_match(guess.artist_guess, solution.artist)
        
        if guess.decade_guess:
            correct_decade = guess.decade_guess.strip() == solution.decade
        
        # Punkte berechnen
        points = 0
        if correct_title:
            points += 3
        if correct_artist:
            points += 2
        if correct_decade:
            points += 1
        
        # Spieler-Score updaten
        player = self._find_player(session_id, guess.player_id)
        if player:
            player.score += points
        
        return GuessResult(
            correct_title=correct_title,
            correct_artist=correct_artist,
            correct_decade=correct_decade,
            points_earned=points,
            total_score=player.score if player else 0,
            correct_answers={
                "title": solution.title,
                "artist": solution.artist,
                "decade": solution.decade
            }
        )
    
    def next_track(self, session_id: str) -> Dict:
        """
        Gehe zum nächsten Track
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} nicht gefunden")
        
        session = self.sessions[session_id]
        tracks = self.track_queues.get(session_id, [])
        
        session.current_track_index += 1
        
        if session.current_track_index >= len(tracks):
            session.status = "finished"
            return {
                "status": "finished",
                "message": "Alle Songs gespielt!",
                "final_scores": self._get_leaderboard(session_id)
            }
        
        # Nächsten Track laden
        current_track = tracks[session.current_track_index]
        self.solutions[session_id] = current_track
        
        return {
            "status": "playing",
            "track_number": session.current_track_index + 1,
            "total_tracks": len(tracks),
            "track": {
                "track_id": current_track.track_id,
                "uri": current_track.uri,
                "duration_ms": current_track.duration_ms
            }
        }
    
    def get_leaderboard(self, session_id: str) -> List[Dict]:
        """
        Hole Leaderboard für Session
        """
        return self._get_leaderboard(session_id)
    
    def _get_leaderboard(self, session_id: str) -> List[Dict]:
        """
        Interne Leaderboard-Funktion
        """
        players = self.players.get(session_id, [])
        sorted_players = sorted(players, key=lambda p: p.score, reverse=True)
        
        return [
            {
                "player_id": p.player_id,
                "name": p.name,
                "score": p.score,
                "rank": idx + 1
            }
            for idx, p in enumerate(sorted_players)
        ]
    
    def _find_player(self, session_id: str, player_id: str) -> Optional[Player]:
        """
        Finde Spieler in Session
        """
        players = self.players.get(session_id, [])
        for player in players:
            if player.player_id == player_id:
                return player
        return None
    
    def _fuzzy_match(self, guess: str, solution: str, threshold: float = 0.8) -> bool:
        """
        Fuzzy String Matching (einfache Version)
        Später: Levenshtein Distance oder difflib
        """
        guess_clean = guess.strip().lower()
        solution_clean = solution.strip().lower()
        
        # Exakte Übereinstimmung
        if guess_clean == solution_clean:
            return True
        
        # Teilstring (z.B. "Bohemian" in "Bohemian Rhapsody")
        if guess_clean in solution_clean or solution_clean in guess_clean:
            return True
        
        # Später: Levenshtein für Tippfehler
        return False


# Singleton Instance
game_service = GameService()
