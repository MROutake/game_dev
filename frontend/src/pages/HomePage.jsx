import { useNavigate } from 'react-router-dom'
import { Music, Users, Sparkles } from 'lucide-react'

function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="flex items-center justify-center mb-6">
            <Music className="w-20 h-20 text-hister-pink animate-pulse" />
            <Sparkles className="w-12 h-12 text-hister-purple ml-2" />
          </div>
          <h1 className="text-7xl font-bold mb-4 bg-gradient-to-r from-hister-purple to-hister-pink bg-clip-text text-transparent">
            Hister 2.0
          </h1>
          <p className="text-2xl text-gray-300">
            � Music Quiz Game
          </p>
        </div>

        {/* Main Actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Spiel Erstellen */}
          <button
            onClick={() => navigate('/create')}
            className="card hover:scale-105 transition-transform duration-300 cursor-pointer group"
          >
            <div className="flex flex-col items-center text-center p-8">
              <div className="w-24 h-24 bg-gradient-to-br from-hister-purple to-hister-pink rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Sparkles className="w-12 h-12" />
              </div>
              <h2 className="text-3xl font-bold mb-3">Spiel Erstellen</h2>
              <p className="text-gray-300">
                Erstelle eine neue Lobby und lade Freunde ein
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Du wirst zum Spielleiter
              </p>
            </div>
          </button>

          {/* Spiel Beitreten */}
          <button
            onClick={() => navigate('/join')}
            className="card hover:scale-105 transition-transform duration-300 cursor-pointer group"
          >
            <div className="flex flex-col items-center text-center p-8">
              <div className="w-24 h-24 bg-gradient-to-br from-pink-500 to-purple-500 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Users className="w-12 h-12" />
              </div>
              <h2 className="text-3xl font-bold mb-3">Spiel Beitreten</h2>
              <p className="text-gray-300">
                Finde verfügbare Lobbys in deinem Netzwerk
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Trete als Mitspieler bei
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default HomePage
