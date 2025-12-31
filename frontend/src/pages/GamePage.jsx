import { useNavigate } from 'react-router-dom'
import { Music } from 'lucide-react'

function GamePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="card max-w-2xl text-center">
        <Music className="w-20 h-20 mx-auto mb-6 text-hister-pink animate-pulse" />
        <h1 className="text-4xl font-bold mb-4">Spiel läuft bald! 🎵</h1>
        <p className="text-gray-300 mb-6">
          Die Game-Seite kommt als nächstes mit:
        </p>
        <ul className="text-left text-gray-300 space-y-2 mb-8 max-w-md mx-auto">
          <li>🎤 Eingabefelder für Titel, Interpret, Jahrzehnt</li>
          <li>⏱️ Timer pro Song</li>
          <li>🏆 Live Scoreboard</li>
          <li>🎵 Spotify Web Playback Integration</li>
        </ul>
        <button
          onClick={() => navigate('/')}
          className="btn-secondary"
        >
          Zurück zur Hauptseite
        </button>
      </div>
    </div>
  )
}

export default GamePage
