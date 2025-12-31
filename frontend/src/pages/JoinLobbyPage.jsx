import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Users, Wifi, Loader, RefreshCw } from 'lucide-react'
import { discoverLobbies, addPlayer } from '../services/api'

function JoinLobbyPage() {
  const navigate = useNavigate()
  const [playerName, setPlayerName] = useState('')
  const [lobbies, setLobbies] = useState([])
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(true)
  const [error, setError] = useState('')
  const [selectedLobby, setSelectedLobby] = useState(null)

  // Lobbys suchen
  const scanForLobbies = async () => {
    setScanning(true)
    setError('')
    
    try {
      console.log('🔍 JoinLobbyPage: Starte Lobby-Scan...')
      const foundLobbies = await discoverLobbies()
      console.log('📋 JoinLobbyPage: Gefundene Lobbies:', foundLobbies)
      setLobbies(foundLobbies)
      
      if (foundLobbies.length === 0) {
        console.warn('⚠️ JoinLobbyPage: Keine Lobbies gefunden!')
        setError('Keine Lobbys gefunden. Stelle sicher, dass jemand ein Spiel erstellt hat.')
      } else {
        console.log(`✅ JoinLobbyPage: ${foundLobbies.length} Lobbies gefunden`)
      }
    } catch (err) {
      console.error('❌ JoinLobbyPage: Fehler beim Scannen:', err)
      setError('Fehler beim Suchen nach Lobbys. Ist das Backend gestartet?')
    } finally {
      setScanning(false)
    }
  }

  useEffect(() => {
    scanForLobbies()
    
    // Auto-refresh alle 5 Sekunden
    const interval = setInterval(scanForLobbies, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleJoinLobby = async (lobby) => {
    if (!playerName.trim()) {
      setError('Bitte gib deinen Namen ein')
      return
    }

    setLoading(true)
    setSelectedLobby(lobby.session_id)
    setError('')

    try {
      const player = await addPlayer(lobby.session_id, playerName.trim())
      console.log('Lobby beigetreten:', player)
      
      // Navigiere zur Lobby
      navigate(`/lobby/${lobby.session_id}`, {
        state: { 
          isHost: false, 
          playerName,
          playerId: player.player_id 
        }
      })
    } catch (err) {
      console.error('Fehler beim Beitreten:', err)
      setError('Fehler beim Beitreten. Versuche es nochmal.')
      setSelectedLobby(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-300 hover:text-white mb-8 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Zurück
        </button>

        {/* Card */}
        <div className="card">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-10 h-10" />
            </div>
            <h1 className="text-4xl font-bold mb-2">Spiel Beitreten</h1>
            <p className="text-gray-300">Wähle eine verfügbare Lobby</p>
          </div>

          {/* Name Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">
              Dein Name
            </label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="z.B. Anna"
              className="input-field"
              maxLength={20}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-lg p-3 text-sm mb-4">
              {error}
            </div>
          )}

          {/* Scan Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center text-sm text-gray-300">
              <Wifi className={`w-4 h-4 mr-2 ${scanning ? 'animate-pulse' : ''}`} />
              {scanning ? 'Suche nach Lobbys...' : `${lobbies.length} Lobby(s) gefunden`}
            </div>
            <button
              onClick={scanForLobbies}
              disabled={scanning}
              className="flex items-center text-sm text-hister-purple hover:text-hister-pink transition-colors"
            >
              <RefreshCw className={`w-4 h-4 mr-1 ${scanning ? 'animate-spin' : ''}`} />
              Aktualisieren
            </button>
          </div>

          {/* Lobbies List */}
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {scanning && lobbies.length === 0 ? (
              <div className="text-center py-12">
                <Loader className="w-12 h-12 mx-auto mb-4 animate-spin text-hister-purple" />
                <p className="text-gray-300">Suche nach verfügbaren Lobbys...</p>
              </div>
            ) : lobbies.length === 0 ? (
              <div className="text-center py-12">
                <Wifi className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                <p className="text-gray-300 mb-2">Keine Lobbys gefunden</p>
                <p className="text-sm text-gray-500">
                  Warte darauf, dass jemand ein Spiel erstellt
                </p>
              </div>
            ) : (
              lobbies.map((lobby) => (
                <div
                  key={lobby.session_id}
                  className="bg-white/5 rounded-xl p-4 border border-white/10 hover:border-hister-purple transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-1">
                        <Users className="w-4 h-4 mr-2 text-hister-purple" />
                        <h3 className="font-bold text-lg">{lobby.host_name}'s Lobby</h3>
                      </div>
                      <div className="text-sm text-gray-400">
                        <span className="inline-flex items-center">
                          👥 {lobby.player_count || 0} Spieler
                        </span>
                        <span className="mx-2">•</span>
                        <span className={`inline-flex items-center ${
                          lobby.status === 'waiting' ? 'text-green-400' : 'text-yellow-400'
                        }`}>
                          {lobby.status === 'waiting' ? '⏳ Wartet' : '🎮 Läuft'}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleJoinLobby(lobby)}
                      disabled={loading || !playerName.trim() || lobby.status !== 'waiting'}
                      className={`px-6 py-2 rounded-lg font-medium transition-all ${
                        lobby.status !== 'waiting'
                          ? 'bg-gray-500/50 cursor-not-allowed'
                          : loading && selectedLobby === lobby.session_id
                          ? 'bg-hister-purple/50'
                          : 'bg-hister-purple hover:bg-hister-pink'
                      }`}
                    >
                      {loading && selectedLobby === lobby.session_id ? (
                        <Loader className="w-5 h-5 animate-spin" />
                      ) : lobby.status !== 'waiting' ? (
                        'Gestartet'
                      ) : (
                        'Beitreten'
                      )}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Network Info */}
        <div className="mt-6 text-center text-sm text-gray-400">
          <p>🌐 Es werden nur Lobbys im lokalen Netzwerk angezeigt</p>
        </div>
      </div>
    </div>
  )
}

export default JoinLobbyPage
