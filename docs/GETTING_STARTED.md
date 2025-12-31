# 🎵 Hister 2.0 - Vollständige Setup-Anleitung

## 📋 Voraussetzungen

- Python 3.9+
- Node.js 18+
- npm oder yarn
- Spotify Premium Account (für Host)

---

## 🚀 Schritt-für-Schritt Setup

### 1️⃣ Backend Setup

```bash
# In das Backend-Verzeichnis wechseln
cd backend

# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Aktivieren (Windows)
# venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# .env Datei erstellen
cp .env.example .env

# .env bearbeiten und Spotify Credentials eintragen
# SPOTIFY_CLIENT_ID=your_client_id_here
# SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

**Spotify Developer App erstellen:**
1. Gehe zu https://developer.spotify.com/dashboard
2. "Create an App"
3. Notiere Client ID & Secret
4. Füge Redirect URI hinzu: `http://localhost:8000/callback`

### 2️⃣ Frontend Setup

```bash
# In das Frontend-Verzeichnis wechseln
cd ../frontend

# Dependencies installieren
npm install

# .env Datei ist bereits vorhanden
# Bei Bedarf anpassen für Netzwerk-Zugriff
```

---

## 🎮 Starten

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate  # oder venv\Scripts\activate (Windows)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend läuft auf: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Frontend läuft auf: `http://localhost:3000`

---

## 🌐 Lokales Netzwerk Setup

### Host-Computer Setup:

1. **Finde deine lokale IP:**
   ```bash
   # Linux/Mac
   hostname -I
   # oder
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```
   
   Beispiel: `192.168.178.42`

2. **Backend mit Host Flag starten:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Environment anpassen:**
   ```env
   # frontend/.env
   VITE_API_URL=http://192.168.178.42:8000
   VITE_SOCKET_URL=http://192.168.178.42:8000
   ```

4. **Frontend neu starten**

### Andere Geräte im Netzwerk:

1. Browser öffnen
2. Gehe zu: `http://192.168.178.42:3000` (Host-IP)
3. Klicke "Spiel Beitreten"
4. Lobbys werden automatisch angezeigt

---

## 🧪 Testing

### Backend testen:
```bash
cd backend
python tests/test_spotify_integration.py
```

### API testen (Browser):
```
http://localhost:8000/docs
```

### Frontend testen:
```
http://localhost:3000
```

---

## 🎯 Verwendung

### Als Host (Spielleiter):

1. Öffne `http://localhost:3000`
2. Klicke **"Spiel Erstellen"**
3. Gib deinen Namen ein
4. Warte auf Mitspieler
5. Klicke **"Spiel Starten"**

### Als Spieler:

1. Öffne `http://192.168.x.x:3000` (Host-IP)
2. Klicke **"Spiel Beitreten"**
3. Wähle eine Lobby
4. Gib deinen Namen ein
5. Warte auf Spielstart

---

## 📝 Aktuelle Features (v2.0-alpha)

✅ **Fertig:**
- Hauptmenü
- Lobby erstellen
- Lobby beitreten
- Lobby-Discovery (lokales Netzwerk)
- Spieler-Management
- Warteraum

🚧 **In Arbeit:**
- Game-Seite (Ratespiel)
- Spotify Web Playback SDK
- Timer-System
- Live-Scoreboard

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
- Ist das Backend gestartet? (`uvicorn app.main:app --reload`)
- Läuft es auf Port 8000? (Check `http://localhost:8000/health`)
- Firewall blockiert den Port?

### "No lobbies found"
- Hat jemand eine Lobby erstellt?
- Sind beide Geräte im gleichen Netzwerk?
- Backend läuft mit `--host 0.0.0.0`?

### "Import errors" in Backend
- Virtual Environment aktiviert?
- Dependencies installiert? (`pip install -r requirements.txt`)

### Frontend lädt nicht
- Dependencies installiert? (`npm install`)
- Port 3000 belegt? (Ändere in `vite.config.js`)

---

## 📦 Projekt-Struktur

```
Hister_2/
├── backend/                # Python FastAPI
│   ├── app/
│   │   ├── api/           # API Endpoints
│   │   ├── services/      # Business Logic
│   │   ├── models/        # Data Models
│   │   └── main.py        # Entry Point
│   ├── tests/
│   └── requirements.txt
│
├── frontend/              # React + Vite
│   ├── src/
│   │   ├── pages/        # Seiten
│   │   ├── services/     # API Client
│   │   ├── hooks/        # Custom Hooks
│   │   └── App.jsx
│   └── package.json
│
├── docs/                  # Dokumentation
└── README.md
```

---

## 🎵 Nächste Schritte

1. ✅ Grundstruktur steht
2. ✅ Backend läuft
3. ✅ Frontend läuft
4. ✅ Lobby-System funktioniert
5. 🔜 Game-Logik implementieren
6. 🔜 Spotify Web Playback integrieren
7. 🔜 Scoring-System
8. 🔜 Timer & Live-Updates

---

## 📞 Support & Fragen

- **Backend API Docs:** http://localhost:8000/docs
- **GitHub Issues:** (falls Repository erstellt)
- **Logs prüfen:** 
  - Backend: Terminal-Output
  - Frontend: Browser DevTools → Console

---

**Viel Spaß beim Spielen! 🎉**
