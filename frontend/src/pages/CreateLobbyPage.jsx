import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Sparkles, Loader } from 'lucide-react'
import { createSession } from '../services/api'

function CreateLobbyPage() {
  const navigate = useNavigate()
  const [hostName, setHostName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCreate = async (e) => {
    e.preventDefault()
    
    if (!hostName.trim()) {
      setError('Bitte gib deinen Namen ein')
      return
    }

    setLoading(true)
    setError('')

    try {
      const session = await createSession(hostName.trim())
      console.log('Session erstellt:', session)
      
      // Navigiere zur Lobby mit Host-Info
      navigate(`/lobby/${session.session_id}`, {
        state: { 
          isHost: true, 
          hostName: hostName.trim(),
          playerId: session.host_player_id || 'host-' + session.session_id
        }
      })
    } catch (err) {
      console.error('Fehler beim Erstellen:', err)
      setError('Fehler beim Erstellen der Lobby. Ist das Backend gestartet?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full">
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
            <div className="w-20 h-20 bg-gradient-to-br from-hister-purple to-hister-pink rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-10 h-10" />
            </div>
            <h1 className="text-4xl font-bold mb-2">Spiel Erstellen</h1>
            <p className="text-gray-300">Du wirst zum Spielleiter</p>
          </div>

          <form onSubmit={handleCreate} className="space-y-6">
            {/* Name Input */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Dein Name
              </label>
              <input
                type="text"
                value={hostName}
                onChange={(e) => setHostName(e.target.value)}
                placeholder="z.B. Max"
                className="input-field"
                autoFocus
                maxLength={20}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-500/20 border border-red-500 rounded-lg p-3 text-sm">
                {error}
              </div>
            )}

            {/* Info */}
            <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-4 text-sm">
              <p className="font-medium mb-2">ℹ️ Als Spielleiter kannst du:</p>
              <ul className="space-y-1 text-gray-300">
                <li>• Playlist auswählen</li>
                <li>• Spiel starten</li>
                <li>• Zum nächsten Song springen</li>
              </ul>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader className="w-6 h-6 mr-2 animate-spin" />
                  Erstelle Lobby...
                </>
              ) : (
                <>
                  <Sparkles className="w-6 h-6 mr-2" />
                  Lobby Erstellen
                </>
              )}
            </button>
          </form>
        </div>

        {/* Network Info */}
        <div className="mt-6 text-center text-sm text-gray-400">
          <p>🌐 Deine Lobby wird im lokalen Netzwerk sichtbar sein</p>
        </div>
      </div>
    </div>
  )
}

export default CreateLobbyPage
