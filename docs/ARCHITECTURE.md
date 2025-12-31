# 🎯 Hister 2.0 - Architektur & Technische Dokumentation

## 🏗️ Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                   │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────┐ │
│  │  Game UI     │  │  Spotify Web   │  │  WebSocket  │ │
│  │  (Ratespiel) │  │  Playback SDK  │  │  (Live)     │ │
│  └──────────────┘  └────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │ HTTP REST API
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                     │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────┐ │
│  │  API Routes  │  │  Game Service  │  │  Spotify    │ │
│  │  (FastAPI)   │  │  (Logic)       │  │  Service    │ │
│  └──────────────┘  └────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               Spotify Web API                           │
│  (Playlists, Tracks, Metadata, Playback Control)        │
└─────────────────────────────────────────────────────────┘
```

## 📁 Projektstruktur

```
Hister_2/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI App Entry Point
│   │   ├── __init__.py
│   │   │
│   │   ├── api/                 # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Spotify OAuth
│   │   │   ├── playlist.py      # Playlist & Track Endpoints
│   │   │   └── game.py          # Game Session & Gameplay
│   │   │
│   │   ├── core/                # Core Configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py        # Settings (Spotify, CORS, etc.)
│   │   │
│   │   ├── models/              # Data Models (Pydantic)
│   │   │   ├── __init__.py
│   │   │   └── game.py          # SpotifyTrack, GameSession, Player
│   │   │
│   │   └── services/            # Business Logic
│   │       ├── __init__.py
│   │       ├── spotify_service.py  # Spotify API Integration
│   │       └── game_service.py     # Game Logic & State
│   │
│   ├── tests/
│   │   └── test_spotify_integration.py
│   │
│   ├── .env                     # Environment Variables (SECRET!)
│   ├── .env.example             # Template
│   └── requirements.txt         # Python Dependencies
│
├── frontend/                    # (später: React App)
│
├── docs/
│   ├── SETUP.md                # Setup Guide
│   └── ARCHITECTURE.md         # Diese Datei
│
├── .gitignore
└── README.md
```

## 🎯 Komponenten-Details

### 1. **Spotify Service** (`spotify_service.py`)

**Verantwortlichkeiten:**
- Spotify OAuth2 Flow
- Playlist-Zugriff
- Track-Metadaten abrufen
- Jahrzehnt-Berechnung

**Wichtige Methoden:**
- `get_auth_url()` - OAuth URL generieren
- `authenticate_with_code(code)` - Access Token holen
- `get_playlist_tracks(playlist_id)` - Alle Tracks einer Playlist
- `get_track_info(track_id)` - Einzelner Track
- `shuffle_tracks(tracks)` - Zufällige Reihenfolge

**Spotify API Scopes:**
```python
"user-read-playback-state"      # Playback Status lesen
"user-modify-playback-state"    # Playback steuern
"playlist-read-private"         # Private Playlists
"playlist-read-collaborative"   # Collaborative Playlists
```

### 2. **Game Service** (`game_service.py`)

**Verantwortlichkeiten:**
- Session-Management
- Spieler-Management
- Track-Queue verwalten
- Guess-Logik & Scoring
- Leaderboard

**State Storage (In-Memory):**
```python
sessions: Dict[session_id, GameSession]
players: Dict[session_id, List[Player]]
track_queues: Dict[session_id, List[SpotifyTrack]]
solutions: Dict[session_id, SpotifyTrack]  # Aktueller Track
```

**Game Flow:**
1. `create_session()` - Session erstellen
2. `add_player()` - Spieler hinzufügen
3. `load_playlist()` - Playlist laden & shuffeln
4. `start_game()` - Ersten Track aktivieren
5. `check_guess()` - Guess prüfen & Punkte vergeben
6. `next_track()` - Nächster Song

**Punktesystem:**
- ✅ Titel korrekt: **3 Punkte**
- ✅ Interpret korrekt: **2 Punkte**
- ✅ Jahrzehnt korrekt: **1 Punkt**

### 3. **API Routes**

#### **Auth Endpoints** (`/auth/*`)
```
GET  /auth/login        → Spotify Auth URL
GET  /auth/callback     → OAuth Callback (automatisch von Spotify)
POST /auth/set-token    → Token manuell setzen
```

#### **Playlist Endpoints** (`/playlist/*`)
```
GET /playlist/{id}           → Playlist Info & Tracks
GET /playlist/track/{id}     → Einzelner Track
GET /playlist/search/tracks  → Tracks suchen
```

#### **Game Endpoints** (`/game/*`)
```
POST /game/session/create          → Neue Session
POST /game/session/player/add      → Spieler hinzufügen
POST /game/session/playlist/load   → Playlist laden
POST /game/start                   → Spiel starten
GET  /game/current-track/{id}      → Aktueller Track (ohne Lösung!)
POST /game/guess                   → Guess abgeben
POST /game/next                    → Nächster Track
GET  /game/leaderboard/{id}        → Scoreboard
```

## 🔐 Spotify OAuth Flow

```
1. Frontend/Client:
   GET /auth/login
   ← { "auth_url": "https://accounts.spotify.com/..." }

2. User öffnet auth_url im Browser
   → Loggt sich bei Spotify ein
   → Akzeptiert Permissions

3. Spotify redirected zu:
   http://localhost:8000/callback?code=ABC123...

4. Backend:
   GET /callback?code=ABC123
   → Tauscht code gegen access_token
   ← { "access_token": "...", "expires_in": 3600 }

5. Frontend speichert access_token
   → Sendet bei jedem Request mit
```

## 🎵 Music Playback (WICHTIG!)

### ❌ Was NICHT funktioniert:
- MP3s streamen vom Backend
- Eigenen Audio-Player bauen
- Musik ohne Spotify Premium abspielen

### ✅ Die Lösung: Spotify Web Playback SDK

**Im Frontend (Browser):**
```javascript
// Spotify Player initialisieren
const player = new Spotify.Player({
    name: 'Hister 2.0',
    getOAuthToken: cb => { cb(access_token); }
});

// Track abspielen
player.play({
    uris: ['spotify:track:TRACK_ID']
});
```

**Backend sendet nur:**
- Track URI: `spotify:track:...`
- Track ID: `...`
- Metadaten: Titel, Interpret, etc.

**Musik spielt direkt von Spotify!**

## 🎲 Zufallswiedergabe-Logik

```python
# 1. Alle Tracks aus Playlist holen
tracks = spotify_service.get_playlist_tracks(playlist_id)

# 2. Mischen
import random
random.shuffle(tracks)

# 3. In Queue speichern
track_queues[session_id] = tracks

# 4. Index tracken
current_index = 0

# 5. Nächster Track
current_index += 1
next_track = tracks[current_index]
```

## 📅 Jahrzehnt-Berechnung

```python
def _get_decade(release_date: str) -> str:
    """
    '1994-08-23' -> '1990er'
    '2003-11-17' -> '2000er'
    """
    year = int(release_date[:4])
    decade_start = (year // 10) * 10
    return f"{decade_start}er"
```

**Beispiele:**
- 1994 → (1994 // 10) * 10 = 1990 → "1990er"
- 2023 → (2023 // 10) * 10 = 2020 → "2020er"

## 🎯 Guess-Matching Logik

```python
def _fuzzy_match(guess: str, solution: str) -> bool:
    guess_clean = guess.strip().lower()
    solution_clean = solution.strip().lower()
    
    # 1. Exakte Übereinstimmung
    if guess_clean == solution_clean:
        return True
    
    # 2. Teilstring
    if guess_clean in solution_clean:
        return True
    
    # 3. Später: Levenshtein Distance für Tippfehler
    return False
```

**Verbesserungen (später):**
- Levenshtein Distance (z.B. "Bohemain" → "Bohemian")
- Aliases (z.B. "MJ" → "Michael Jackson")
- Artikel ignorieren ("The Beatles" = "Beatles")

## 🔄 Session State Machine

```
waiting → playing → finished
   ↓         ↓          ↓
[create] [start]   [all tracks done]
```

**Stati:**
- `waiting`: Session erstellt, warte auf Spieler & Playlist
- `playing`: Spiel läuft
- `finished`: Alle Tracks gespielt

## 📊 Datenmodelle

### SpotifyTrack
```python
{
    "track_id": "3n3Ppam7vgaVa1iaRUc9Lp",
    "title": "Mr. Brightside",
    "artist": "The Killers",
    "album": "Hot Fuss",
    "release_date": "2004-06-07",
    "decade": "2000er",
    "duration_ms": 222973,
    "uri": "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp"
}
```

### GameSession
```python
{
    "session_id": "abc-123",
    "host_name": "Max",
    "playlist_id": "37i9dQZF1DX...",
    "current_track_index": 0,
    "status": "playing",
    "started_at": "2025-12-30T..."
}
```

### GuessResult
```python
{
    "correct_title": true,
    "correct_artist": true,
    "correct_decade": false,
    "points_earned": 5,
    "total_score": 23,
    "correct_answers": {
        "title": "Mr. Brightside",
        "artist": "The Killers",
        "decade": "2000er"
    }
}
```

## 🚀 Deployment (später)

### Backend
- **Platform**: Railway, Render, Fly.io
- **Database**: PostgreSQL (statt SQLite)
- **Environment**: Production `.env`

### Frontend
- **Platform**: Vercel, Netlify
- **Build**: Next.js / React
- **Spotify SDK**: Im Browser

## 🔒 Sicherheit

✅ **Wichtig:**
- `.env` NIEMALS committen!
- Access Tokens sicher speichern
- CORS richtig konfigurieren
- Rate Limiting (später)

## 🎮 Multiplayer Architecture

**Host-Modell (empfohlen):**
```
1 Host → logged bei Spotify ein
Alle anderen → spielen ohne Spotify Account
```

**WebSocket Updates:**
- Neuer Track
- Spieler-Guess
- Score-Update
- Leaderboard-Änderung

## 📝 TODOs & Erweiterungen

- [ ] Database (SQLite → PostgreSQL)
- [ ] WebSockets für Live-Updates
- [ ] Frontend (React + Spotify SDK)
- [ ] Besseres Fuzzy-Matching
- [ ] Timer pro Track
- [ ] Hints-System
- [ ] Custom Playlists (Songs hinzufügen)
- [ ] Achievements
- [ ] Statistiken

---

**Version:** 2.0.0  
**Stand:** 30.12.2025
