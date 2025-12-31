# 🎵 Hister 2.0 - Setup Guide

## 🚀 Quick Start

### 1. Spotify Developer App erstellen

1. Gehe zu [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Klicke auf "Create an App"
3. Name: "Hister 2.0" (oder beliebig)
4. Description: "Music Quiz Game"
5. Klicke "Create"
6. Notiere dir **Client ID** und **Client Secret**
7. Klicke "Edit Settings"
8. Unter "Redirect URIs" füge hinzu: `http://localhost:8000/callback`
9. Speichern

### 2. Backend Setup

```bash
cd backend

# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Aktivieren (Windows)
# venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# .env Datei bearbeiten
# Trage deine Spotify Credentials ein
nano .env  # oder code .env
```

### 3. .env Konfiguration

Öffne `backend/.env` und fülle aus:

```env
SPOTIFY_CLIENT_ID=deine_client_id_hier
SPOTIFY_CLIENT_SECRET=dein_client_secret_hier
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback
```

### 4. Test der Spotify Integration

```bash
cd backend
python tests/test_spotify_integration.py
```

Dieser Test:
- ✅ Prüft die Config
- ✅ Generiert eine Auth URL
- ✅ Testet die Jahrzehnt-Berechnung
- ✅ Versucht eine Playlist zu laden

### 5. Backend starten

```bash
cd backend
uvicorn app.main:app --reload
```

Backend läuft dann auf: `http://localhost:8000`

API Docs: `http://localhost:8000/docs`

## 📖 API Endpoints

### Authentication
- `GET /auth/login` - Spotify Login URL
- `GET /auth/callback` - OAuth Callback
- `POST /auth/set-token` - Token manuell setzen

### Playlist
- `GET /playlist/{playlist_id}` - Playlist laden
- `GET /playlist/track/{track_id}` - Track Info
- `GET /playlist/search/tracks` - Tracks suchen

### Game
- `POST /game/session/create` - Session erstellen
- `POST /game/session/player/add` - Spieler hinzufügen
- `POST /game/session/playlist/load` - Playlist laden
- `POST /game/start` - Spiel starten
- `GET /game/current-track/{session_id}` - Aktueller Track
- `POST /game/guess` - Guess abgeben
- `POST /game/next` - Nächster Track
- `GET /game/leaderboard/{session_id}` - Scoreboard

## 🎮 Spielablauf (API Flow)

### 1. Session erstellen
```bash
POST /game/session/create
{
  "host_name": "Max"
}
```

### 2. Spieler hinzufügen
```bash
POST /game/session/player/add
{
  "session_id": "...",
  "player_name": "Anna"
}
```

### 3. Playlist laden
```bash
POST /game/session/playlist/load
{
  "session_id": "...",
  "playlist_id": "37i9dQZF1DXcBWIGoYBM5M"
}
```

### 4. Spiel starten
```bash
POST /game/start?session_id=...
```

### 5. Guess abgeben
```bash
POST /game/guess
{
  "session_id": "...",
  "player_id": "...",
  "title_guess": "Bohemian Rhapsody",
  "artist_guess": "Queen",
  "decade_guess": "1970er"
}
```

### 6. Nächster Song
```bash
POST /game/next
{
  "session_id": "..."
}
```

## 🧪 Testing

### Mit curl
```bash
# Health Check
curl http://localhost:8000/health

# Auth URL
curl http://localhost:8000/auth/login

# Playlist (öffentlich)
curl http://localhost:8000/playlist/37i9dQZF1DXcBWIGoYBM5M
```

### Mit API Docs
Öffne `http://localhost:8000/docs` und teste interaktiv!

## 🔍 Troubleshooting

### "Import could not be resolved"
Das ist normal vor der Installation. Nach `pip install -r requirements.txt` verschwinden die Fehler.

### "SPOTIFY_CLIENT_ID not set"
- Prüfe ob `.env` Datei existiert
- Prüfe ob Credentials eingetragen sind
- Backend neu starten

### "Playlist not found"
- Prüfe ob Playlist öffentlich ist
- Oder: Authentifiziere dich zuerst über `/auth/login`

## 📝 Nächste Schritte

1. ✅ Backend läuft
2. 🔜 Frontend (React + Spotify Web Playback SDK)
3. 🔜 WebSockets für Live-Updates
4. 🔜 Deployment (z.B. Vercel + Railway)

## 💡 Tipps

- **Test-Playlist**: Spotify's "Today's Top Hits" ist öffentlich: `37i9dQZF1DXcBWIGoYBM5M`
- **Debug-Mode**: In `.env` steht `DEBUG=True` - alle Errors werden detailliert angezeigt
- **CORS**: Frontend kann von `localhost:3000` zugreifen
