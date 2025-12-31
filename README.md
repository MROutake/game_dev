# 🎵 Hister 2.0 - Music Quiz Game

Ein interaktives Musik-Ratespiel mit Spotify-Integration für lokales Multiplayer.

## 🎯 Features

- 🎤 **Song-Quiz**: Rate Titel, Interpret und Jahrzehnt
- 👥 **Multiplayer**: Spiele mit Freunden lokal
- 🎲 **Zufallswiedergabe**: Songs werden gemischt
- 🏆 **Punktesystem**: Echtzeit-Scoring
- 🎧 **Spotify Integration**: Nutzt Spotify Web Playback SDK

## 📋 Voraussetzungen

- Python 3.9+
- Spotify Premium Account (für Host)
- Node.js 18+ (für Frontend)
- Spotify Developer App (Client ID & Secret)

## 🚀 Installation

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Spotify API Setup

1. Gehe zu [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Erstelle eine neue App
3. Notiere **Client ID** und **Client Secret**
4. Füge `http://localhost:8000/callback` als Redirect URI hinzu
5. Erstelle `.env` Datei (siehe `.env.example`)

### Starten

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend (später)
cd frontend
npm install
npm run dev
```

## 📁 Projektstruktur

```
Hister_2/
├── backend/
│   ├── app/
│   │   ├── api/          # API Endpoints
│   │   ├── core/         # Config & Settings
│   │   ├── models/       # Data Models
│   │   └── services/     # Business Logic (Spotify, Game)
│   ├── tests/            # Unit Tests
│   └── requirements.txt
├── frontend/             # React App (später)
└── docs/                 # Dokumentation
```

## 🎮 Spielablauf

1. Host startet Session und logged sich bei Spotify ein
2. Spieler fügen Songs zur gemeinsamen Playlist hinzu
3. Songs werden zufällig gemischt und abgespielt
4. Spieler raten Titel, Interpret & Jahrzehnt
5. Punkte werden in Echtzeit angezeigt

## 🔐 Wichtig: Rechtliches

✅ Musik wird über Spotify Web Playback SDK abgespielt  
✅ Nur Metadaten werden gespeichert  
❌ Keine MP3s werden heruntergeladen oder gespeichert  
❌ Nur für privaten Gebrauch mit Freunden

## 📖 API Dokumentation

Nach dem Start verfügbar unter: `http://localhost:8000/docs`

## 🛠️ Tech Stack

**Backend:**
- FastAPI
- Spotipy (Spotify API Client)
- Python 3.9+

**Frontend:**
- React / Next.js
- Spotify Web Playback SDK
- WebSockets (für Live-Updates)

## 📝 Lizenz

Privates Projekt - Nur für den persönlichen Gebrauch
