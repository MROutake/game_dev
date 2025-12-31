import { useState } from 'react'
import { SkipForward, UserX, ShoppingCart, Coins } from 'lucide-react'

/**
 * TokenActions - UI für HITSTER Token-Aktionen
 * - Skip Song (1 Token)
 * - Steal Card (1 Token + Guess)
 * - Buy Card (3 Token)
 */
function TokenActions({ 
  tokens = 0, 
  onSkipSong, 
  onStealCard, 
  onBuyCard,
  disabled = false,
  otherPlayers = []
}) {
  const [showStealDialog, setShowStealDialog] = useState(false)
  const [selectedPlayer, setSelectedPlayer] = useState(null)
  const [selectedPosition, setSelectedPosition] = useState(0)
  const [titleGuess, setTitleGuess] = useState('')
  const [artistGuess, setArtistGuess] = useState('')

  const handleSkipClick = () => {
    if (tokens < 1) {
      alert('⚠️ Nicht genug Token! Benötigt: 1 Token')
      return
    }
    if (window.confirm('🎵 Song für 1 Token überspringen?')) {
      onSkipSong()
    }
  }

  const handleStealClick = () => {
    if (tokens < 1) {
      alert('⚠️ Nicht genug Token! Benötigt: 1 Token')
      return
    }
    if (otherPlayers.length === 0) {
      alert('⚠️ Keine anderen Spieler zum Bestehlen!')
      return
    }
    setShowStealDialog(true)
  }

  const handleStealSubmit = () => {
    if (!selectedPlayer) {
      alert('⚠️ Bitte wähle einen Spieler!')
      return
    }
    if (!titleGuess || !artistGuess) {
      alert('⚠️ Bitte gib Titel und Künstler ein!')
      return
    }

    onStealCard({
      target_player_id: selectedPlayer.player_id,
      target_position: selectedPosition,
      title_guess: titleGuess,
      artist_guess: artistGuess
    })

    // Reset
    setShowStealDialog(false)
    setSelectedPlayer(null)
    setSelectedPosition(0)
    setTitleGuess('')
    setArtistGuess('')
  }

  const handleBuyClick = () => {
    if (tokens < 3) {
      alert('⚠️ Nicht genug Token! Benötigt: 3 Token')
      return
    }
    if (window.confirm('💳 Karte für 3 Token kaufen? (automatisch korrekt platziert)')) {
      onBuyCard()
    }
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <Coins className="w-5 h-5 text-hister-pink" />
          HITSTER Token
        </h3>
        <div className="text-2xl font-bold text-hister-pink">
          {tokens} 🎟️
        </div>
      </div>

      <div className="space-y-3">
        {/* Skip Song */}
        <button
          onClick={handleSkipClick}
          disabled={disabled || tokens < 1}
          className="w-full flex items-center justify-between p-4 rounded-lg
                   bg-gray-800 hover:bg-gray-700 transition-colors
                   disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="flex items-center gap-3">
            <SkipForward className="w-5 h-5 text-blue-400" />
            <div className="text-left">
              <div className="font-semibold text-white">Song überspringen</div>
              <div className="text-xs text-gray-400">Nächster Track</div>
            </div>
          </div>
          <div className="text-sm font-semibold text-blue-400">1 🎟️</div>
        </button>

        {/* Steal Card */}
        <button
          onClick={handleStealClick}
          disabled={disabled || tokens < 1 || otherPlayers.length === 0}
          className="w-full flex items-center justify-between p-4 rounded-lg
                   bg-gray-800 hover:bg-gray-700 transition-colors
                   disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="flex items-center gap-3">
            <UserX className="w-5 h-5 text-red-400" />
            <div className="text-left">
              <div className="font-semibold text-white">Karte stehlen</div>
              <div className="text-xs text-gray-400">Titel + Künstler raten</div>
            </div>
          </div>
          <div className="text-sm font-semibold text-red-400">1 🎟️</div>
        </button>

        {/* Buy Card */}
        <button
          onClick={handleBuyClick}
          disabled={disabled || tokens < 3}
          className="w-full flex items-center justify-between p-4 rounded-lg
                   bg-gray-800 hover:bg-gray-700 transition-colors
                   disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="flex items-center gap-3">
            <ShoppingCart className="w-5 h-5 text-green-400" />
            <div className="text-left">
              <div className="font-semibold text-white">Karte kaufen</div>
              <div className="text-xs text-gray-400">Automatisch korrekt</div>
            </div>
          </div>
          <div className="text-sm font-semibold text-green-400">3 🎟️</div>
        </button>
      </div>

      {/* Info Text */}
      <div className="mt-4 p-3 bg-gray-800 rounded-lg">
        <p className="text-xs text-gray-400">
          💡 Token-Tipp: Spare Token für wichtige Momente! Bei Steal Card wird der Token auch bei
          Fehlversuch abgezogen.
        </p>
      </div>

      {/* Steal Card Dialog */}
      {showStealDialog && (
        <StealCardDialog
          players={otherPlayers}
          selectedPlayer={selectedPlayer}
          setSelectedPlayer={setSelectedPlayer}
          selectedPosition={selectedPosition}
          setSelectedPosition={setSelectedPosition}
          titleGuess={titleGuess}
          setTitleGuess={setTitleGuess}
          artistGuess={artistGuess}
          setArtistGuess={setArtistGuess}
          onSubmit={handleStealSubmit}
          onCancel={() => setShowStealDialog(false)}
        />
      )}
    </div>
  )
}

/**
 * StealCardDialog - Modal für Karten-Diebstahl
 */
function StealCardDialog({
  players,
  selectedPlayer,
  setSelectedPlayer,
  selectedPosition,
  setSelectedPosition,
  titleGuess,
  setTitleGuess,
  artistGuess,
  setArtistGuess,
  onSubmit,
  onCancel
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="card max-w-md w-full p-6">
        <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <UserX className="w-6 h-6 text-red-400" />
          Karte stehlen
        </h3>

        <div className="space-y-4">
          {/* Spieler wählen */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Von welchem Spieler?
            </label>
            <select
              value={selectedPlayer?.player_id || ''}
              onChange={(e) => {
                const player = players.find(p => p.player_id === e.target.value)
                setSelectedPlayer(player)
                setSelectedPosition(0) // Reset Position
              }}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg
                       text-white focus:outline-none focus:border-hister-pink"
            >
              <option value="">-- Spieler wählen --</option>
              {players.map(player => (
                <option key={player.player_id} value={player.player_id}>
                  {player.name} ({player.score || 0} Karten)
                </option>
              ))}
            </select>
          </div>

          {/* Position wählen */}
          {selectedPlayer && selectedPlayer.score > 0 && (
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Welche Karte? (Position)
              </label>
              <select
                value={selectedPosition}
                onChange={(e) => setSelectedPosition(parseInt(e.target.value))}
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg
                         text-white focus:outline-none focus:border-hister-pink"
              >
                {Array.from({ length: selectedPlayer.score }, (_, i) => (
                  <option key={i} value={i}>
                    Position {i + 1} (von {selectedPlayer.score})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Titel Guess */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Titel der Karte
            </label>
            <input
              type="text"
              value={titleGuess}
              onChange={(e) => setTitleGuess(e.target.value)}
              placeholder="z.B. Bohemian Rhapsody"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg
                       text-white placeholder-gray-500
                       focus:outline-none focus:border-hister-pink"
            />
          </div>

          {/* Künstler Guess */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Künstler der Karte
            </label>
            <input
              type="text"
              value={artistGuess}
              onChange={(e) => setArtistGuess(e.target.value)}
              placeholder="z.B. Queen"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg
                       text-white placeholder-gray-500
                       focus:outline-none focus:border-hister-pink"
            />
          </div>

          {/* Warnung */}
          <div className="p-3 bg-red-900 bg-opacity-30 border border-red-700 rounded-lg">
            <p className="text-xs text-red-300">
              ⚠️ Achtung: Der Token wird auch bei Fehlversuch abgezogen!
            </p>
          </div>

          {/* Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onCancel}
              className="flex-1 btn-secondary"
            >
              Abbrechen
            </button>
            <button
              onClick={onSubmit}
              disabled={!selectedPlayer || !titleGuess || !artistGuess}
              className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Stehlen 🎟️
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TokenActions
