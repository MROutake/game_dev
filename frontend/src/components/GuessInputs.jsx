import { useState } from 'react'
import { Music, User, Calendar } from 'lucide-react'

/**
 * GuessInputs - Eingabefelder für Titel, Künstler, Jahr
 * Je nach Spielmodus werden unterschiedliche Felder angezeigt
 */
function GuessInputs({ gameMode = 'original', onSubmit, disabled = false }) {
  const [titleGuess, setTitleGuess] = useState('')
  const [artistGuess, setArtistGuess] = useState('')
  const [yearGuess, setYearGuess] = useState('')

  const showGuessInputs = gameMode === 'pro' || gameMode === 'expert'
  const showYearInput = gameMode === 'expert'

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      title_guess: titleGuess || null,
      artist_guess: artistGuess || null,
      year_guess: yearGuess ? parseInt(yearGuess) : null
    })
    
    // Reset nach Submit
    setTitleGuess('')
    setArtistGuess('')
    setYearGuess('')
  }

  if (!showGuessInputs) {
    return null // Im ORIGINAL Modus keine Inputs
  }

  return (
    <div className="card p-6 mb-6">
      <h3 className="text-xl font-bold mb-4 flex items-center">
        <Music className="w-5 h-5 mr-2 text-hister-pink" />
        Rate den Song für +1 Token!
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Titel Input */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            Titel
          </label>
          <input
            type="text"
            value={titleGuess}
            onChange={(e) => setTitleGuess(e.target.value)}
            placeholder="z.B. Bohemian Rhapsody"
            disabled={disabled}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg
                     text-white placeholder-gray-500
                     focus:outline-none focus:border-hister-pink
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Künstler Input */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            Künstler
          </label>
          <input
            type="text"
            value={artistGuess}
            onChange={(e) => setArtistGuess(e.target.value)}
            placeholder="z.B. Queen"
            disabled={disabled}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg
                     text-white placeholder-gray-500
                     focus:outline-none focus:border-hister-pink
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Jahr Input (nur EXPERT) */}
        {showYearInput && (
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Jahr (EXPERT Modus)
            </label>
            <input
              type="number"
              value={yearGuess}
              onChange={(e) => setYearGuess(e.target.value)}
              placeholder="z.B. 1975"
              min="1900"
              max="2025"
              disabled={disabled}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg
                       text-white placeholder-gray-500
                       focus:outline-none focus:border-hister-pink
                       disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
        )}

        {/* Info Text */}
        <p className="text-xs text-gray-500">
          {gameMode === 'pro' && '💡 Titel + Künstler richtig = +1 Token'}
          {gameMode === 'expert' && '💡 Titel + Künstler + Jahr richtig = +1 Token'}
        </p>
      </form>
    </div>
  )
}

export default GuessInputs
