# 🎵 Hister 2.0 - Frontend

React-basierte Webapp für das Musik-Ratespiel.

## 🚀 Quick Start

```bash
# Dependencies installieren
npm install

# Development Server starten
npm run dev

# App öffnet sich auf: http://localhost:3000
```

## 📁 Struktur

```
src/
├── pages/              # Seiten
│   ├── HomePage.jsx           # Hauptmenü
│   ├── CreateLobbyPage.jsx    # Spiel erstellen
│   ├── JoinLobbyPage.jsx      # Spiel beitreten
│   ├── LobbyPage.jsx          # Warteraum
│   └── GamePage.jsx           # Spielseite
├── components/         # Wiederverwendbare Komponenten
├── services/          # API & Backend Communication
│   └── api.js
├── hooks/             # Custom React Hooks
│   └── useWebSocket.js
├── App.jsx            # Main App mit Routing
├── main.jsx           # Entry Point
└── index.css          # Global Styles (Tailwind)
```

## 🎮 Features

### Hauptseite
- ✨ **Spiel Erstellen**: Werde zum Spielleiter
- 👥 **Spiel Beitreten**: Finde Lobbys im lokalen Netzwerk

### Lobby (Warteraum)
- 📋 Spielerliste (Live-Updates)
- 👑 Spielleiter kann Spiel starten
- 🌐 WebSocket-basierte Synchronisation

### Game (Kommt noch)
- 🎤 Eingabefelder (Titel, Interpret, Jahrzehnt)
- ⏱️ Timer
- 🏆 Live-Scoreboard
- 🎵 Spotify Playback

## 🔧 Technologien

- **React 18** - UI Framework
- **Vite** - Build Tool & Dev Server
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Socket.IO** - WebSockets für Live-Updates
- **Axios** - HTTP Client
- **Lucide React** - Icons

## 🌐 Lokales Netzwerk

Die App ist für **lokales Multiplayer** ausgelegt:

1. **Host startet Backend & Frontend**
2. **Andere Geräte im gleichen Netzwerk** können auf die IP zugreifen:
   ```
   http://192.168.x.x:3000
   ```
3. **Lobby Discovery** zeigt alle verfügbaren Spiele

### IP-Adresse finden:

```bash
# Linux/Mac
hostname -I

# Windows
ipconfig
```

## 📝 Environment Variables

Erstelle `.env` (siehe `.env.example`):

```env
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

Für Netzwerk-Zugriff:
```env
VITE_API_URL=http://192.168.x.x:8000
VITE_SOCKET_URL=http://192.168.x.x:8000
```

## 🎨 Styling

Tailwind CSS mit Custom Theme:

```js
// tailwind.config.js
colors: {
  'hister-purple': '#8B5CF6',
  'hister-pink': '#EC4899',
  'hister-dark': '#1F2937',
}
```

Custom Classes:
- `.btn-primary` - Gradient Button
- `.btn-secondary` - Secondary Button
- `.card` - Glassmorphism Card
- `.input-field` - Input mit Backdrop

## 🔌 API Integration

```js
import { createSession, addPlayer, discoverLobbies } from './services/api'

// Session erstellen
const session = await createSession('Max')

// Spieler hinzufügen
const player = await addPlayer(sessionId, 'Anna')

// Lobbys finden
const lobbies = await discoverLobbies()
```

## 🌊 WebSocket Events

```js
const { connected, sendMessage } = useWebSocket(sessionId, {
  onPlayerJoined: (player) => console.log('Neuer Spieler:', player),
  onGameStarted: () => navigate('/game'),
  onNewTrack: (track) => console.log('Neuer Song:', track),
  onGuessResult: (result) => console.log('Ergebnis:', result),
})
```

## 🚧 TODOs

- [x] Hauptseite
- [x] Lobby Erstellen
- [x] Lobby Beitreten
- [x] Lobby-Verwaltung
- [ ] Game-Seite
- [ ] Spotify Web Playback SDK
- [ ] Timer-System
- [ ] Live-Scoreboard
- [ ] Mobile Responsiveness
- [ ] Sound Effects

## 📱 Mobile Support

Die App ist responsive designed:
- 📱 Mobile-First Approach
- 📐 Flexibles Grid-Layout
- 👆 Touch-optimierte Buttons

## 🐛 Debugging

```bash
# Console Logs prüfen
# Browser DevTools -> Console

# Network Requests
# Browser DevTools -> Network

# React DevTools installieren
# Chrome Extension: React Developer Tools
```

## 🎯 Production Build

```bash
npm run build
# Output: dist/

npm run preview
# Preview Production Build
```

---

**Version:** 2.0.0  
**Framework:** React 18 + Vite
