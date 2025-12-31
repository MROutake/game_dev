import { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, Users, Play, Loader, Crown, Music } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'
import { getSessionPlayers } from '../services/api'

function LobbyPage() {
  const { sessionId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  
  const isHost = location.state?.isHost || false
  const playerName = location.state?.playerName || location.state?.hostName || 'Spieler'
  const playerId = location.state?.playerId
  
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingPlayers, setLoadingPlayers] = useState(true)

  // WebSocket für Live-Updates
  const { connected, socket } = useWebSocket(sessionId, {
    onPlayerJoined: (player) => {
      console.log('👤 Spieler beigetreten:', player)
      setPlayers(prev => {
        // Prüfe ob Spieler schon existiert
        if (prev.some(p => p.player_id === player.player_id)) {
          return prev
        }
        return [...prev, { ...player, isHost: false }]
      })
    },
    onPlayerLeft: (data) => {
      console.log('👋 Spieler verlassen:', data)
      setPlayers(prev => prev.filter(p => p.player_id !== data.player_id))
      
      // Wenn Host verlassen hat, zurück zur Startseite
      if (data.was_host && !isHost) {
        alert('Der Spielleiter hat die Lobby verlassen')
        navigate('/')
      }
    },
    onGameStarted: () => {
      navigate(`/game/${sessionId}`)
    },
    onSessionClosed: (data) => {
      console.log('🚪 Session geschlossen:', data)
      alert(data.message || 'Die Lobby wurde geschlossen')
      navigate('/')
    }
  })

  // Lade initiale Spielerliste
  useEffect(() => {
    let mounted = true
    
    const loadPlayers = async () => {
      try {
        console.log('🔄 Lade Spieler für Session:', sessionId)
        const response = await getSessionPlayers(sessionId)
        console.log('📋 API Response:', response)
        
        if (!mounted) return
        
        if (!response.players) {
          console.warn('⚠️ Keine Spieler in der Response')
          setPlayers([])
          setLoadingPlayers(false)
          return
        }
        
        // Markiere Host (erster Spieler oder basierend auf Namen)
        const playersWithHost = response.players.map((p, idx) => ({
          ...p,
          isHost: idx === 0 || p.name === playerName
        }))
        
        console.log('✅ Spieler mit Host-Flag:', playersWithHost)
        setPlayers(playersWithHost)
        setLoadingPlayers(false)
      } catch (err) {
        console.error('❌ Fehler beim Laden der Spieler:', err)
        if (mounted) {
          setLoadingPlayers(false)
        }
      }
    }
    
    if (sessionId) {
      loadPlayers()
      // Aktualisiere alle 2 Sekunden als Fallback
      const interval = setInterval(loadPlayers, 2000)
      return () => {
        mounted = false
        clearInterval(interval)
      }
    }
  }, [sessionId, playerName])

  // Tritt Lobby bei via WebSocket
  useEffect(() => {
    if (connected && socket && sessionId) {
      console.log('🔌 Trete Lobby bei via WebSocket...')
      socket.emit('join_lobby', {
        session_id: sessionId,
        player_name: playerName,
        player_id: playerId
      })
    }
  }, [connected, socket, sessionId, playerName, playerId])

  const handleStartGame = async () => {
    if (!isHost) return
    
    setLoading(true)
    try {
      if (socket) {
        socket.emit('start_game', { session_id: sessionId })
      }
      
      setTimeout(() => {
        navigate(`/game/${sessionId}`)
      }, 1000)
    } catch (err) {
      console.error('Fehler beim Starten:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loadingPlayers) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 mx-auto mb-4 animate-spin text-hister-purple" />
          <p className="text-gray-300">Lade Lobby...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-3xl w-full">
        {/* Back Button (nur für Non-Host) */}
        {!isHost && (
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-300 hover:text-white mb-8 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Verlassen
          </button>
        )}

        {/* Main Card */}
        <div className="card">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <Music className="w-12 h-12 text-hister-pink" />
            </div>
            <h1 className="text-4xl font-bold mb-2">Lobby</h1>
            <p className="text-gray-300">
              {isHost ? '🎮 Du bist der Spielleiter' : `🎯 Warte auf Spielleiter...`}
            </p>
            
            {/* Connection Status */}
            <div className="flex items-center justify-center mt-3 text-sm">
              <div className={`w-2 h-2 rounded-full mr-2 ${
                connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
              }`} />
              <span className="text-gray-400">
                {connected ? 'Verbunden' : 'Verbindung wird hergestellt...'}
              </span>
            </div>
          </div>

          {/* Players List */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Spieler ({players.length})
              </h2>
            </div>

            <div className="space-y-3 max-h-64 overflow-y-auto">
              {players.map((player, index) => (
                <div
                  key={player.player_id}
                  className="bg-white/5 rounded-xl p-4 border border-white/10 flex items-center justify-between"
                >
                  <div className="flex items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-3 ${
                      player.isHost 
                        ? 'bg-gradient-to-br from-yellow-400 to-orange-500' 
                        : 'bg-gradient-to-br from-hister-purple to-hister-pink'
                    }`}>
                      {player.isHost ? (
                        <Crown className="w-5 h-5" />
                      ) : (
                        <span className="font-bold">{index + 1}</span>
                      )}
                    </div>
                    <div>
                      <div className="font-bold flex items-center">
                        {player.name}
                        {player.isHost && (
                          <span className="ml-2 text-xs bg-yellow-500/20 px-2 py-0.5 rounded">
                            Spielleiter
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-400">
                        Bereit
                      </div>
                    </div>
                  </div>
                  <div className="text-2xl">
                    {player.isHost ? '👑' : '✨'}
                  </div>
                </div>
              ))}
            </div>

            {/* Waiting Message */}
            {players.length === 1 && (
              <div className="mt-4 text-center text-gray-400 text-sm">
                <p>⏳ Warte auf weitere Spieler...</p>
              </div>
            )}
          </div>

          {/* Host Controls */}
          {isHost ? (
            <div className="space-y-4">
              {/* Info */}
              <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-4 text-sm">
                <p className="font-medium mb-2">ℹ️ Bevor du startest:</p>
                <ul className="space-y-1 text-gray-300">
                  <li>• Warte auf mindestens einen Mitspieler</li>
                  <li>• Stelle sicher, dass Spotify läuft</li>
                  <li>• Du kannst später eine Playlist auswählen</li>
                </ul>
              </div>

              {/* Start Button */}
              <button
                onClick={handleStartGame}
                disabled={loading || players.length < 1}
                className="btn-primary w-full flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader className="w-6 h-6 mr-2 animate-spin" />
                    Starte Spiel...
                  </>
                ) : (
                  <>
                    <Play className="w-6 h-6 mr-2" />
                    Spiel Starten
                  </>
                )}
              </button>
            </div>
          ) : (
            /* Player waiting */
            <div className="text-center py-8">
              <Loader className="w-12 h-12 mx-auto mb-4 animate-spin text-hister-purple" />
              <p className="text-gray-300">Warte auf Spielstart...</p>
              <p className="text-sm text-gray-500 mt-2">
                Der Spielleiter wird das Spiel bald starten
              </p>
            </div>
          )}
        </div>

        {/* Session Info */}
        <div className="mt-6 text-center text-xs text-gray-500">
          <p>Session ID: {sessionId.slice(0, 8)}...</p>
        </div>
      </div>
    </div>
  )
}

export default LobbyPage
