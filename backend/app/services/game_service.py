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
    GuessResult,
    TimelineCard,
    PlacementRequest,
    PlacementResult,
    GameMode,
    TokenActionType,
    TokenActionRequest,
    TokenActionResult
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
    
    def create_session(self, host_name: str, playlist_id: Optional[str] = None, game_mode: GameMode = GameMode.ORIGINAL) -> GameSession:
        """
        Erstelle neue Game Session
        """
        session_id = str(uuid.uuid4())
        
        # Token-Anzahl je nach Modus
        token_count = {
            GameMode.ORIGINAL: 2,
            GameMode.PRO: 5,
            GameMode.EXPERT: 3,
            GameMode.TEAMWORK: 10
        }.get(game_mode, 2)
        
        session = GameSession(
            session_id=session_id,
            host_name=host_name,
            playlist_id=playlist_id,
            current_track_index=0,
            status="waiting",
            game_mode=game_mode,
            win_condition=10,
            round_number=0
        )
        
        self.sessions[session_id] = session
        self.players[session_id] = []
        
        # Host automatisch als ersten Spieler hinzufügen
        host_player = Player(
            player_id=str(uuid.uuid4()),
            name=host_name,
            score=0,
            session_id=session_id,
            tokens=token_count,
            timeline=[],
            has_won=False
        )
        self.players[session_id].append(host_player)
        
        return session
    
    def add_player(self, session_id: str, player_name: str) -> Player:
        """
        Füge Spieler zur Session hinzu
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} nicht gefunden")
        
        session = self.sessions[session_id]
        
        # Token-Anzahl je nach Modus
        token_count = {
            GameMode.ORIGINAL: 2,
            GameMode.PRO: 5,
            GameMode.EXPERT: 3,
            GameMode.TEAMWORK: 10
        }.get(session.game_mode, 2)
        
        player_id = str(uuid.uuid4())
        player = Player(
            player_id=player_id,
            name=player_name,
            score=0,
            session_id=session_id,
            tokens=token_count,
            timeline=[],
            has_won=False
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
        session.round_number = 1
        
        # Gebe jedem Spieler eine Start-Karte
        players = self.players.get(session_id, [])
        num_start_cards = len(players)
        
        self.give_start_card(session_id)
        
        # Setze current_track_index NACH den Start-Karten
        session.current_track_index = num_start_cards
        
        # Ersten Spieler setzen
        if len(players) > 0:
            session.current_player_turn = players[0].player_id
        
        # Ersten Track für Gameplay laden (nicht die Start-Karten)
        if session.current_track_index < len(self.track_queues[session_id]):
            current_track = self.track_queues[session_id][session.current_track_index]
            self.solutions[session_id] = current_track
        
        return {
            "session_id": session_id,
            "status": "playing",
            "total_tracks": len(self.track_queues[session_id]),
            "current_track_index": session.current_track_index,
            "current_player": session.current_player_turn,
            "game_mode": session.game_mode.value,
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
    
    # =====================================================
    # TIMELINE-SYSTEM (HITSTER Original)
    # =====================================================
    
    def place_card_in_timeline(self, placement: PlacementRequest) -> PlacementResult:
        """
        Platziere aktuelle Karte in Spieler-Timeline
        Prüfe ob Position korrekt ist (HITSTER Kernmechanik)
        """
        session_id = placement.session_id
        player_id = placement.player_id
        position = placement.position
        
        if session_id not in self.solutions:
            raise ValueError("Kein aktiver Track für diese Session")
        
        player = self._find_player(session_id, player_id)
        if not player:
            raise ValueError(f"Spieler {player_id} nicht gefunden")
        
        session = self.sessions[session_id]
        current_track = self.solutions[session_id]
        track_year = int(current_track.release_date[:4])
        
        # Prüfe ob Position in Timeline korrekt ist
        is_correct = self._check_timeline_position(
            player.timeline,
            position,
            track_year
        )
        
        # Token-Check (PRO/EXPERT Modus)
        earned_token = False
        if is_correct and session.game_mode in [GameMode.PRO, GameMode.EXPERT]:
            # PRO: Titel + Künstler müssen stimmen
            if placement.title_guess and placement.artist_guess:
                title_correct = self._fuzzy_match(placement.title_guess, current_track.title)
                artist_correct = self._fuzzy_match(placement.artist_guess, current_track.artist)
                
                if session.game_mode == GameMode.EXPERT:
                    # EXPERT: Auch Jahr muss stimmen
                    year_correct = placement.year_guess == track_year
                    if title_correct and artist_correct and year_correct:
                        earned_token = True
                        player.tokens += 1
                elif title_correct and artist_correct:
                    earned_token = True
                    player.tokens += 1
        
        if is_correct:
            # Füge Karte zur Timeline hinzu
            new_card = TimelineCard(
                position=position,
                track_id=current_track.track_id,
                title=current_track.title,
                artist=current_track.artist,
                year=track_year,
                is_correct=True
            )
            
            player.timeline.insert(position, new_card)
            
            # Aktualisiere Positionen aller nachfolgenden Karten
            for i in range(position + 1, len(player.timeline)):
                player.timeline[i].position = i
            
            player.score += 1  # Score = Anzahl Karten in Timeline
            
            # Prüfe Gewinnbedingung
            if player.score >= session.win_condition:
                player.has_won = True
                session.status = "finished"
                return PlacementResult(
                    correct=True,
                    won_game=True,
                    new_score=player.score,
                    earned_token=earned_token,
                    correct_year=track_year,
                    correct_title=current_track.title,
                    correct_artist=current_track.artist,
                    player_timeline=player.timeline
                )
        
        return PlacementResult(
            correct=is_correct,
            won_game=False,
            new_score=player.score,
            earned_token=earned_token,
            correct_year=track_year,
            correct_title=current_track.title,
            correct_artist=current_track.artist,
            player_timeline=player.timeline if is_correct else []
        )
    
    def _check_timeline_position(
        self, 
        timeline: List[TimelineCard], 
        position: int, 
        year: int
    ) -> bool:
        """
        Prüfe ob das Jahr an die richtige Position in der Timeline passt
        
        Timeline ist aufsteigend sortiert (älteste links, neueste rechts)
        """
        # Leere Timeline: Immer korrekt
        if len(timeline) == 0:
            return position == 0
        
        # Position 0: Song muss älter oder gleich alt wie timeline[0] sein
        if position == 0:
            return year <= timeline[0].year
        
        # Position am Ende: Song muss neuer oder gleich alt wie letzter sein
        if position == len(timeline):
            return year >= timeline[-1].year
        
        # Mittendrin: Jahr muss zwischen links und rechts liegen
        if 0 < position < len(timeline):
            left_year = timeline[position - 1].year
            right_year = timeline[position].year
            return left_year <= year <= right_year
        
        return False
    
    def get_player_timeline(self, session_id: str, player_id: str) -> List[TimelineCard]:
        """
        Hole Timeline eines Spielers
        """
        player = self._find_player(session_id, player_id)
        if not player:
            raise ValueError(f"Spieler {player_id} nicht gefunden")
        return player.timeline
    
    def give_start_card(self, session_id: str) -> None:
        """
        Gebe jedem Spieler eine Start-Karte (automatisch korrekt platziert)
        Wird beim Spielstart aufgerufen
        """
        if session_id not in self.track_queues:
            raise ValueError("Keine Tracks geladen")
        
        players = self.players.get(session_id, [])
        tracks = self.track_queues[session_id]
        
        for idx, player in enumerate(players):
            if idx < len(tracks):
                track = tracks[idx]
                year = int(track.release_date[:4])
                
                start_card = TimelineCard(
                    position=0,
                    track_id=track.track_id,
                    title=track.title,
                    artist=track.artist,
                    year=year,
                    is_correct=True
                )
                
                player.timeline = [start_card]
                player.score = 1
                
                print(f"📍 Spieler {player.name} erhält Start-Karte: {track.title} ({year})")
    
    # =====================================================
    # TOKEN-SYSTEM (HITSTER Actions)
    # =====================================================
    
    def use_token_action(self, action: TokenActionRequest) -> TokenActionResult:
        """
        Führe Token-Aktion aus
        """
        player = self._find_player(action.session_id, action.player_id)
        if not player:
            raise ValueError(f"Spieler {action.player_id} nicht gefunden")
        
        if action.action_type == TokenActionType.SKIP_SONG:
            return self._token_skip_song(action.session_id, player)
        
        elif action.action_type == TokenActionType.STEAL_CARD:
            return self._token_steal_card(action, player)
        
        elif action.action_type == TokenActionType.BUY_CARD:
            return self._token_buy_card(action.session_id, player)
        
        else:
            raise ValueError(f"Unbekannter Action Type: {action.action_type}")
    
    def _token_skip_song(self, session_id: str, player: Player) -> TokenActionResult:
        """
        Token-Aktion 1: Song überspringen (1 Token)
        """
        if player.tokens < 1:
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=player.tokens,
                message="Nicht genug Token! Benötigt: 1 Token"
            )
        
        # Token abziehen
        player.tokens -= 1
        
        # Nächsten Song laden
        try:
            next_result = self.next_track(session_id)
            
            return TokenActionResult(
                success=True,
                tokens_spent=1,
                new_token_count=player.tokens,
                message=f"Song übersprungen! Nächster Song geladen."
            )
        except Exception as e:
            # Token zurückgeben bei Fehler
            player.tokens += 1
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=player.tokens,
                message=f"Fehler beim Überspringen: {str(e)}"
            )
    
    def _token_steal_card(self, action: TokenActionRequest, thief: Player) -> TokenActionResult:
        """
        Token-Aktion 2: Karte stehlen (1 Token + Guess)
        """
        if thief.tokens < 1:
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=thief.tokens,
                message="Nicht genug Token! Benötigt: 1 Token"
            )
        
        # Validiere Input
        if not action.target_player_id or action.target_position is None:
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=thief.tokens,
                message="Ziel-Spieler und Position müssen angegeben werden!"
            )
        
        if not action.title_guess or not action.artist_guess:
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=thief.tokens,
                message="Titel und Künstler müssen geraten werden!"
            )
        
        # Finde Ziel-Spieler
        target = self._find_player(action.session_id, action.target_player_id)
        if not target:
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=thief.tokens,
                message="Ziel-Spieler nicht gefunden!"
            )
        
        # Prüfe ob Ziel-Karte existiert
        if action.target_position >= len(target.timeline):
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=thief.tokens,
                message="Karte an dieser Position existiert nicht!"
            )
        
        # Hole Ziel-Karte
        stolen_card = target.timeline[action.target_position]
        
        # Prüfe Guess
        title_correct = self._fuzzy_match(action.title_guess, stolen_card.title)
        artist_correct = self._fuzzy_match(action.artist_guess, stolen_card.artist)
        
        session = self.sessions.get(action.session_id)
        year_correct = True  # Default für nicht-EXPERT Modus
        
        if session and session.game_mode == GameMode.EXPERT:
            if action.year_guess:
                year_correct = action.year_guess == stolen_card.year
            else:
                year_correct = False
        
        # Prüfe ob Diebstahl erfolgreich
        success = title_correct and artist_correct and year_correct
        
        # Token IMMER abziehen (auch bei Fehlversuch)
        thief.tokens -= 1
        
        if success:
            # Entferne Karte von Ziel-Spieler
            target.timeline.pop(action.target_position)
            target.score -= 1
            
            # Füge Karte zu Dieb hinzu (am Ende)
            thief.timeline.append(stolen_card)
            thief.score += 1
            
            # Positionen aktualisieren
            for i, card in enumerate(target.timeline):
                card.position = i
            for i, card in enumerate(thief.timeline):
                card.position = i
            
            return TokenActionResult(
                success=True,
                tokens_spent=1,
                new_token_count=thief.tokens,
                message=f"🎉 Diebstahl erfolgreich! '{stolen_card.title}' gestohlen!",
                stolen_card=stolen_card
            )
        else:
            return TokenActionResult(
                success=False,
                tokens_spent=1,
                new_token_count=thief.tokens,
                message=f"❌ Diebstahl fehlgeschlagen! Falscher Guess. (Token verloren)"
            )
    
    def _token_buy_card(self, session_id: str, player: Player) -> TokenActionResult:
        """
        Token-Aktion 3: Karte kaufen (3 Token = 1 gratis Karte)
        """
        if player.tokens < 3:
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=player.tokens,
                message="Nicht genug Token! Benötigt: 3 Token"
            )
        
        if session_id not in self.track_queues:
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=player.tokens,
                message="Keine Tracks verfügbar!"
            )
        
        session = self.sessions[session_id]
        tracks = self.track_queues[session_id]
        
        # Nehme nächsten Track
        if session.current_track_index >= len(tracks):
            return TokenActionResult(
                success=False,
                tokens_spent=0,
                new_token_count=player.tokens,
                message="Keine weiteren Songs verfügbar!"
            )
        
        current_track = tracks[session.current_track_index]
        year = int(current_track.release_date[:4])
        
        # Token abziehen
        player.tokens -= 3
        
        # Erstelle Karte
        bought_card = TimelineCard(
            position=len(player.timeline),
            track_id=current_track.track_id,
            title=current_track.title,
            artist=current_track.artist,
            year=year,
            is_correct=True
        )
        
        # Füge automatisch korrekt hinzu (sortiert nach Jahr)
        # Finde richtige Position
        insert_position = 0
        for i, card in enumerate(player.timeline):
            if year >= card.year:
                insert_position = i + 1
        
        player.timeline.insert(insert_position, bought_card)
        player.score += 1
        
        # Positionen aktualisieren
        for i, card in enumerate(player.timeline):
            card.position = i
        
        # Nächsten Track für andere
        session.current_track_index += 1
        
        return TokenActionResult(
            success=True,
            tokens_spent=3,
            new_token_count=player.tokens,
            message=f"✅ Karte gekauft: '{current_track.title}' ({year})",
            stolen_card=bought_card
        )


# Singleton Instance
game_service = GameService()
# Singleton Instance
game_service = GameService()
