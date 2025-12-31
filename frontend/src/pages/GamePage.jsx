import { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { Music, Trophy, Coins, ArrowLeft } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'
import { placeCard, getPlayerTimeline, getSessionPlayers, nextTrack } from '../services/api'
import Timeline from '../components/Timeline'
import GuessInputs from '../components/GuessInputs'

function GamePage() {
  const { sessionId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  
  const playerId = location.state?.playerId
  const playerName = location.state?.playerName || 'Spieler'
  const isHost = location.state?.isHost || false
  
  const [myTimeline, setMyTimeline] = useState([])
  const [players, setPlayers] = useState([])
  const [currentTrack, setCurrentTrack] = useState(null)
  const [isMyTurn, setIsMyTurn] = useState(false)
  const [gameMode, setGameMode] = useState('original')
  const [myTokens, setMyTokens] = useState(2)
  const [selectedPosition, setSelectedPosition] = useState(null)
  const [guessData, setGuessData] = useState({})
  const [placementResult, setPlacementResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // WebSocket für Live-Updates
  const { connected } = useWebSocket(sessionId, {
    onCardPlaced: (data) => {
      console.log('🎴 Karte platziert:', data)
      if (data.player_id === playerId) {
        loadMyTimeline()
      }
      loadPlayers()
    },
    onGameWon: (data) => {
      console.log('🏆 Spieler hat gewonnen:', data)
      alert(`${data.player_name || 'Ein Spieler'} hat gewonnen! 🎉`)
    }
  })

  // Lade Timeline beim Start
  useEffect(() => {
    if (sessionId && playerId) {
      loadMyTimeline()
      loadPlayers()
    }
  }, [sessionId, playerId])

  const loadMyTimeline = async () => {
    try {
      const timeline = await getPlayerTimeline(sessionId, playerId)
      setMyTimeline(timeline)
    } catch (err) {
      console.error('❌ Fehler beim Laden der Timeline:', err)
    }
  }

  const loadPlayers = async () => {
    try {
      const response = await getSessionPlayers(sessionId)
      setPlayers(response.players || [])
      
      // Finde eigene Token-Anzahl
      const me = response.players?.find(p => p.player_id === playerId)
      if (me) {
        setMyTokens(me.tokens || 0)
      }
    } catch (err) {
      console.error('❌ Fehler beim Laden der Spieler:', err)
    }
  }

  const handlePlaceCard = async (position) => {
    setSelectedPosition(position)
    
    // Im ORIGINAL Modus direkt platzieren (ohne Guess)
    if (gameMode === 'original') {
      await submitPlacement(position, {})
    }
    // Im PRO/EXPERT: Warte auf Guess-Submit
  }

  const handleGuessSubmit = async (guess) => {
    if (selectedPosition === null) {
      alert('Bitte wähle zuerst eine Position in der Timeline!')
      return
    }
    
    await submitPlacement(selectedPosition, guess)
  }

  const submitPlacement = async (position, guess) => {
    setLoading(true)
    try {
      const result = await placeCard({
        session_id: sessionId,
        player_id: playerId,
        position: position,
        ...guess
      })
      
      console.log('✅ Placement Result:', result)
      setPlacementResult(result)
      
      // Zeige Ergebnis
      if (result.correct) {
        alert(`🎉 Richtig! ${result.correct_title} (${result.correct_year}) 
${result.earned_token ? '🎟️ +1 Token verdient!' : ''}`)
        loadMyTimeline()
      } else {
        alert(`❌ Falsch! Es war: ${result.correct_title} von ${result.correct_artist} (${result.correct_year})`)
      }
      
      // Nächster Track
      if (isHost) {
        await nextTrack(sessionId)
      }
      
      setSelectedPosition(null)
      setGuessData({})
      
    } catch (err) {
      console.error('❌ Fehler beim Platzieren:', err)
      alert('Fehler beim Platzieren der Karte')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-4">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => navigate('/')}
            className="btn-secondary flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Verlassen
          </button>
          
          <div className="flex items-center gap-6">
            {/* Score */}
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              <span className="text-white font-bold">
                {myTimeline.length} / 10 Karten
              </span>
            </div>
            
            {/* Tokens */}
            <div className="flex items-center gap-2">
              <Coins className="w-5 h-5 text-hister-pink" />
              <span className="text-white font-bold">
                {myTokens} Token
              </span>
            </div>
          </div>
        </div>

        {/* Player Info */}
        <div className="card p-4 mb-4">
          <h2 className="text-xl font-bold text-white mb-2">
            {playerName} {isHost && '👑'}
          </h2>
          <p className="text-gray-400 text-sm">
            Modus: <span className="text-hister-pink font-semibold">{gameMode.toUpperCase()}</span>
            {isMyTurn ? ' • 🎯 Du bist dran!' : ' • ⏳ Warte auf anderen Spieler'}
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        {/* Current Track (Placeholder) */}
        <div className="card p-6 mb-6 text-center">
          <Music className="w-12 h-12 mx-auto mb-4 text-hister-pink animate-pulse" />
          <p className="text-gray-400">
            🎵 Song spielt... (Spotify Playback kommt in Phase 4)
          </p>
        </div>

        {/* Guess Inputs (PRO/EXPERT) */}
        <GuessInputs 
          gameMode={gameMode}
          onSubmit={handleGuessSubmit}
          disabled={loading || !isMyTurn || selectedPosition === null}
        />

        {/* Meine Timeline */}
        <div className="card p-6 mb-6">
          <h3 className="text-2xl font-bold mb-4 flex items-center">
            🎴 Meine Timeline
            {selectedPosition !== null && (
              <span className="ml-4 text-sm text-hister-pink">
                → Platziere an Position {selectedPosition}
              </span>
            )}
          </h3>
          
          <Timeline 
            cards={myTimeline}
            onPlaceCard={handlePlaceCard}
            isMyTurn={true}
            canPlaceCard={!loading}
          />
        </div>

        {/* Andere Spieler (Miniatur) */}
        <div className="card p-6">
          <h3 className="text-xl font-bold mb-4">👥 Andere Spieler</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {players
              .filter(p => p.player_id !== playerId)
              .map(player => (
                <div key={player.player_id} className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-white">{player.name}</span>
                    <span className="text-sm text-gray-400">
                      {player.score || 0} Karten
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    🎟️ {player.tokens || 0} Token
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GamePage
