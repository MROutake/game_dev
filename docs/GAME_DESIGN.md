# 🎮 Hister 2.0 - Game Design & Implementierungs-Roadmap

## 📊 Aktueller Status (31.12.2025)

### ✅ Implementiert
- ✅ **Backend-Architektur**: FastAPI mit Socket.IO
- ✅ **Spotify Integration**: OAuth, Playlist-Zugriff, Metadaten
- ✅ **Lobby-System**: Host/Spieler-Rollen, Lobby-Discovery im lokalen Netzwerk
- ✅ **WebSocket**: Real-time Updates (Spieler join/leave, Session-Management)
- ✅ **Frontend-Grundstruktur**: React, Routing, Tailwind CSS
- ✅ **Session-Management**: In-Memory Sessions, Spieler-Verwaltung
- ✅ **Punktesystem (Backend)**: 3 Punkte (Titel) + 2 Punkte (Künstler) + 1 Punkt (Jahrzehnt)

### 🚧 Teilweise implementiert
- 🟡 **Game Service**: Basis-Logik vorhanden, aber an ORIGINAL-Regeln anpassen
- 🟡 **Guess-System**: Fuzzy-Matching implementiert, aber PRO/EXPERT-Modus fehlt

### ❌ Noch nicht implementiert
- ❌ **GamePage UI**: Komplett placeholder
- ❌ **Timeline-System**: Kernmechanik des Originals
- ❌ **Token-System**: HITSTER-Token-Logik
- ❌ **Spielmodi**: ORIGINAL, PRO, EXPERT, TEAMWORK
- ❌ **Spotify Web Playback SDK**: Musik-Wiedergabe
- ❌ **Timer-System**: Zeit pro Track

---

## 🎯 Original HITSTER-Regeln Analyse

### Kernmechanik: Timeline-System

**Im Original:**
```
Jeder Spieler hat eine eigene Zeitleiste mit Karten
├─ Älteste Karte (links)
├─ Mittlere Karten
└─ Neueste Karte (rechts)

Neue Karte wird ZWISCHEN oder NEBEN bestehende Karten platziert
```

**Für digitale Umsetzung:**
```javascript
timeline: [
  { position: 0, track_id: "...", year: 1975 },
  { position: 1, track_id: "...", year: 1989 },
  { position: 2, track_id: "...", year: 2003 }
]

// Spieler platziert neue Karte an Position 2 (zwischen 1989 und 2003)
// Wenn Song von 1996: ✅ Richtig
// Wenn Song von 2010: ❌ Falsch
```

### Punktesystem-Anpassung

**Aktuelles System (falsch für HITSTER):**
- ❌ 3 Punkte Titel
- ❌ 2 Punkte Künstler
- ❌ 1 Punkt Jahrzehnt

**ORIGINAL HITSTER-Regeln:**
- ✅ **Karte richtig platziert** → Karte bleibt in Timeline (= 1 Punkt implizit)
- ✅ **Titel + Künstler genannt** → +1 HITSTER-Token
- ✅ **Gewinnen bei 10 Karten**

**PRO-Modus:**
- ✅ **Karte richtig + Titel + Künstler** → Karte bleibt
- ✅ Start mit 5 Token (statt 2)
- ❌ Keine neuen Token verdienen

**EXPERT-Modus:**
- ✅ **Karte richtig + Titel + Künstler + Exaktes Jahr** → Karte bleibt
- ✅ Start mit 3 Token
- ❌ Keine neuen Token verdienen

---

## 🔧 Erforderliche Änderungen am Datenmodell

### 1. Erweiterte Player-Klasse

```python
class Player(BaseModel):
    player_id: str
    name: str
    score: int = 0  # Anzahl richtig platzierter Karten
    session_id: str
    
    # NEU für HITSTER:
    tokens: int = 2  # HITSTER-Token (2 bei ORIGINAL, 5 bei PRO, 3 bei EXPERT)
    timeline: List[TimelineCard] = []  # Eigene Zeitleiste
    has_won: bool = False
```

### 2. Neue Timeline-Klasse

```python
class TimelineCard(BaseModel):
    position: int  # Position in der Timeline (0 = älteste)
    track_id: str
    year: int  # Nur das Jahr, nicht das komplette Datum
    is_correct: bool = True  # Wurde richtig platziert?
```

### 3. Erweiterte GameSession

```python
class GameSession(BaseModel):
    session_id: str
    host_name: str
    playlist_id: Optional[str] = None
    current_track_index: int = 0
    started_at: Optional[datetime] = None
    status: str = "waiting"
    
    # NEU:
    game_mode: str = "original"  # original, pro, expert, teamwork
    win_condition: int = 10  # Anzahl Karten zum Gewinnen
    current_player_turn: Optional[str] = None  # player_id des Spielers am Zug
    round_number: int = 0
```

### 4. Neue Placement-Request

```python
class PlacementRequest(BaseModel):
    session_id: str
    player_id: str
    position: int  # Wo soll die Karte platziert werden?
    
    # Optional: Titel/Künstler-Guess für Token
    title_guess: Optional[str] = None
    artist_guess: Optional[str] = None
    year_guess: Optional[int] = None  # Nur bei EXPERT
```

### 5. Token-Actions

```python
class TokenAction(BaseModel):
    action_type: str  # "skip_song", "steal_card", "buy_card"
    session_id: str
    player_id: str
    
    # Für "steal_card":
    target_player_id: Optional[str] = None
    target_position: Optional[int] = None
    
    # Für Diebstahl-Guess:
    title_guess: Optional[str] = None
    artist_guess: Optional[str] = None
    year_guess: Optional[int] = None
```

---

## 🎮 Spielablauf-Implementierung

### Phase 1: Session Setup
```
1. Host erstellt Lobby ✅
2. Spieler treten bei ✅
3. Host wählt Spielmodus (ORIGINAL/PRO/EXPERT/TEAMWORK) ❌
4. Host wählt Playlist ❌
5. Jeder Spieler erhält 1 Start-Karte ❌
```

### Phase 2: Spielzug (Rundenbasiert)
```
1. DJ (Host) scannt nächste Karte → Song spielt ab ❌
2. Spieler am Zug wählt Position in seiner Timeline ❌
3. Optional: Spieler gibt Titel/Künstler an (für Token) ❌
4. Karte wird aufgedeckt (Jahr wird gezeigt) ❌
5. Prüfung:
   - Richtig platziert? → Karte bleibt ✅
   - Falsch platziert? → Karte wird abgelegt ❌
   - Titel+Künstler richtig? → +1 Token ❌
6. Andere Spieler können "HITSTER!" rufen (Token-Steal) ❌
7. Nächster Spieler ist dran ❌
```

### Phase 3: Gewinnen
```
- Erste Spieler mit 10 Karten gewinnt ❌
- TEAMWORK: Erreiche 10 Karten bevor Token aufgebraucht ❌
```

---

## 📝 Implementierungs-Roadmap

### Milestone 1: Timeline-System (Priorität: HOCH)

**Backend:**
```python
# game_service.py
def place_card_in_timeline(
    session_id: str,
    player_id: str,
    position: int
) -> PlacementResult:
    """
    Platziere aktuelle Karte in Spieler-Timeline
    Prüfe ob Position korrekt ist
    """
    player = self._find_player(session_id, player_id)
    current_track = self.solutions[session_id]
    track_year = int(current_track.release_date[:4])
    
    # Prüfe ob Position korrekt ist
    is_correct = self._check_timeline_position(
        player.timeline,
        position,
        track_year
    )
    
    if is_correct:
        # Füge Karte zur Timeline hinzu
        player.timeline.insert(position, TimelineCard(
            position=position,
            track_id=current_track.track_id,
            year=track_year
        ))
        player.score += 1  # Score = Anzahl Karten
        
        # Prüfe Gewinnbedingung
        if player.score >= 10:
            player.has_won = True
            return PlacementResult(
                correct=True,
                won_game=True,
                new_score=player.score
            )
    
    return PlacementResult(
        correct=is_correct,
        won_game=False,
        new_score=player.score
    )

def _check_timeline_position(
    timeline: List[TimelineCard],
    position: int,
    year: int
) -> bool:
    """
    Prüfe ob das Jahr an die richtige Position passt
    """
    # Position 0: Song muss älter als timeline[0] sein
    if position == 0 and len(timeline) > 0:
        return year <= timeline[0].year
    
    # Position len(timeline): Song muss neuer als letzter sein
    if position == len(timeline) and len(timeline) > 0:
        return year >= timeline[-1].year
    
    # Mittendrin: Jahr muss zwischen links und rechts liegen
    if 0 < position < len(timeline):
        left_year = timeline[position - 1].year
        right_year = timeline[position].year
        return left_year <= year <= right_year
    
    return True  # Leere Timeline
```

**Frontend: Timeline-Visualisierung**
```jsx
// TimelineComponent.jsx
function Timeline({ cards, onPlaceCard }) {
  return (
    <div className="timeline-container flex overflow-x-auto">
      {/* Insert-Button ganz links */}
      <PlacementSlot position={0} onClick={() => onPlaceCard(0)} />
      
      {/* Alle Karten mit Insert-Buttons dazwischen */}
      {cards.map((card, idx) => (
        <>
          <TimelineCard 
            key={card.track_id}
            title={card.title}
            artist={card.artist}
            year={card.year}
          />
          <PlacementSlot 
            position={idx + 1} 
            onClick={() => onPlaceCard(idx + 1)} 
          />
        </>
      ))}
    </div>
  )
}
```

### Milestone 2: Token-System

**Backend:**
```python
def use_token_skip_song(session_id: str, player_id: str):
    """Token 1: Song überspringen"""
    player = self._find_player(session_id, player_id)
    if player.tokens < 1:
        raise ValueError("Nicht genug Token")
    
    player.tokens -= 1
    # Nächsten Song laden
    return self.next_track(session_id)

def use_token_steal_card(
    session_id: str,
    thief_id: str,
    target_player_id: str,
    position: int,
    title_guess: str,
    artist_guess: str
) -> StealResult:
    """Token 2: Karte stehlen"""
    thief = self._find_player(session_id, thief_id)
    if thief.tokens < 1:
        raise ValueError("Nicht genug Token")
    
    # Prüfe ob Guess korrekt
    solution = self.solutions[session_id]
    correct_title = self._fuzzy_match(title_guess, solution.title)
    correct_artist = self._fuzzy_match(artist_guess, solution.artist)
    
    if correct_title and correct_artist:
        # Diebstahl erfolgreich!
        thief.tokens -= 1
        # Karte wird dem Dieb gegeben
        # ... (Timeline-Logik)
        return StealResult(success=True, token_kept=True)
    else:
        # Diebstahl fehlgeschlagen
        thief.tokens -= 1
        return StealResult(success=False, token_kept=False)

def use_token_buy_card(session_id: str, player_id: str):
    """Token 3: 3 Token = 1 gratis Karte"""
    player = self._find_player(session_id, player_id)
    if player.tokens < 3:
        raise ValueError("Benötigt 3 Token")
    
    player.tokens -= 3
    # Oberste Karte vom Stapel nehmen
    # Automatisch korrekt platzieren (ohne Guess)
```

### Milestone 3: Spielmodi

```python
class GameMode(Enum):
    ORIGINAL = "original"  # Nur Timeline
    PRO = "pro"           # Timeline + Titel + Künstler
    EXPERT = "expert"     # Timeline + Titel + Künstler + Jahr
    TEAMWORK = "teamwork" # Kooperativ, gemeinsame Timeline

def check_placement_with_mode(
    mode: GameMode,
    placement: PlacementRequest,
    solution: SpotifyTrack
) -> PlacementResult:
    """Prüfe Platzierung je nach Spielmodus"""
    
    if mode == GameMode.ORIGINAL:
        # Nur Timeline-Position prüfen
        return check_timeline_position(...)
    
    elif mode == GameMode.PRO:
        # Timeline + Titel + Künstler müssen stimmen
        timeline_ok = check_timeline_position(...)
        title_ok = fuzzy_match(placement.title_guess, solution.title)
        artist_ok = fuzzy_match(placement.artist_guess, solution.artist)
        
        return timeline_ok and title_ok and artist_ok
    
    elif mode == GameMode.EXPERT:
        # Alles + exaktes Jahr
        year_ok = placement.year_guess == int(solution.release_date[:4])
        return timeline_ok and title_ok and artist_ok and year_ok
```

### Milestone 4: GamePage UI

**Komponenten:**
```jsx
// GamePage.jsx
<div className="game-container">
  {/* Aktueller Song-Player */}
  <CurrentTrackDisplay track={currentTrack} />
  
  {/* Spieler-Timeline */}
  <Timeline 
    cards={myTimeline}
    onPlaceCard={handlePlaceCard}
  />
  
  {/* Guess-Inputs (je nach Modus) */}
  {mode === 'pro' || mode === 'expert' ? (
    <GuessInputs 
      onSubmit={handleGuess}
      showYear={mode === 'expert'}
    />
  ) : null}
  
  {/* Token-Aktionen */}
  <TokenActions 
    tokens={myTokens}
    onSkip={handleSkip}
    onSteal={handleSteal}
    onBuy={handleBuy}
  />
  
  {/* Andere Spieler (Miniatur-Timelines) */}
  <OtherPlayers players={otherPlayers} />
  
  {/* Scoreboard */}
  <Scoreboard players={allPlayers} />
</div>
```

### Milestone 5: Spotify Web Playback

```javascript
// SpotifyPlayer.jsx
useEffect(() => {
  window.onSpotifyWebPlaybackSDKReady = () => {
    const player = new Spotify.Player({
      name: 'Hister 2.0',
      getOAuthToken: cb => { cb(accessToken); },
      volume: 0.5
    });
    
    player.addListener('ready', ({ device_id }) => {
      console.log('Device ID:', device_id);
      setDeviceId(device_id);
    });
    
    player.connect();
  };
}, [accessToken]);

// Song abspielen
const playTrack = async (uri) => {
  await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
    method: 'PUT',
    body: JSON.stringify({ uris: [uri] }),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    }
  });
};
```

---

## 🎯 Priorisierte To-Do-Liste

### Phase 1: Core Game Loop (1-2 Wochen)
1. ✅ Timeline-Datenmodell im Backend
2. ✅ `place_card_in_timeline()` Funktion
3. ✅ Timeline-UI Component (Frontend)
4. ✅ Platzierungs-Logik testen
5. ✅ Gewinn-Bedingung (10 Karten)

### Phase 2: Token-System (1 Woche)
1. ✅ Token-Zähler in Player-Model
2. ✅ Token-Aktionen implementieren
3. ✅ Token-UI (Buttons, Anzeige)
4. ✅ HITSTER-Rufen Mechanik

### Phase 3: Spielmodi (3-4 Tage)
1. ✅ Modus-Auswahl beim Erstellen
2. ✅ PRO/EXPERT Guess-Validierung
3. ✅ TEAMWORK kooperativer Modus
4. ✅ Token-Start-Anzahl je Modus

### Phase 4: Musik-Wiedergabe (1 Woche)
1. ✅ Spotify Web Playback SDK integrieren
2. ✅ OAuth für Spieler (nur Host braucht Premium)
3. ✅ Play/Pause/Next Controls
4. ✅ Track-Synchronisation über WebSocket

### Phase 5: Polish & Testing (1 Woche)
1. ✅ Timer pro Track
2. ✅ Animationen (Karten-Flip, Timeline-Insert)
3. ✅ Sound Effects
4. ✅ Mobile Optimierung
5. ✅ Multi-Device Testing

---

## 📊 Technische Herausforderungen

### 1. Timeline-Insertion-Visualisierung
**Problem**: Wie zeigt man interaktiv "Zwischen welche Karten soll platziert werden?"

**Lösung**: Drag-and-Drop oder "+"" Buttons zwischen Karten

### 2. Real-Time Synchronisation
**Problem**: Alle Spieler müssen den gleichen Spielstand sehen

**Lösung**: WebSocket-Events für jede Aktion
```javascript
// Events:
- 'card_placed' → Update aller Timelines
- 'token_used' → Update Token-Counts
- 'hitster_called' → Diebstahl-Attempt
- 'game_won' → Gewinner-Anzeige
```

### 3. Token-Diebstahl Race Condition
**Problem**: Mehrere Spieler rufen gleichzeitig "HITSTER!"

**Lösung**: Server-seitiger Timestamp + Warteschlange
```python
# Erster Client, der Event sendet, gewinnt
steal_attempts = []  # [(timestamp, player_id)]
steal_attempts.sort(key=lambda x: x[0])
first_caller = steal_attempts[0][1]
```

### 4. Spotify Premium Requirement
**Problem**: Nur Host mit Premium kann Musik abspielen

**Lösung**: 
- Host = DJ (spielt ab)
- Alle anderen hören mit (Shared Session)
- Oder: Preview-URLs nutzen (30s Snippets, kein Premium nötig)

---

## 🎨 UI/UX Mockups (Konzept)

### Timeline-Darstellung
```
┌────────────────────────────────────────────┐
│           Meine Timeline (5/10)            │
├────────────────────────────────────────────┤
│                                            │
│  [+]  [1975]  [+]  [1989]  [+]  [2003] [+]│
│       Queen      Beatles      Eminem       │
│                                            │
│  👆 Klicke auf [+] um Karte zu platzieren  │
└────────────────────────────────────────────┘
```

### Token-Anzeige
```
┌─────────────────┐
│ HITSTER-Token   │
│  🎟️ 🎟️ ⚫️        │
│  (2/5)          │
│                 │
│ [Skip Song]     │
│ [Steal Card]    │
│ [Buy Card] (3🎟️) │
└─────────────────┘
```

### Guess-Input (PRO/EXPERT)
```
┌──────────────────────────────┐
│ Rate den Song:               │
│ Titel:   [_____________]     │
│ Künstler: [_____________]    │
│ Jahr:    [____] (EXPERT)     │
│                              │
│       [Platzieren]           │
└──────────────────────────────┘
```

---

## 🚀 Nächste Sofort-Schritte

1. **Heute**: Timeline-Datenmodell im Backend erweitern
2. **Morgen**: `place_card_in_timeline()` implementieren + Tests
3. **Tag 3**: Timeline-UI Component in React
4. **Tag 4**: Integration Backend ↔ Frontend
5. **Tag 5**: Erste spielbare Version testen

---

**Version**: 2.0.0  
**Stand**: 31.12.2025  
**Status**: 🟡 In aktiver Entwicklung
