import { Plus } from 'lucide-react'
import TimelineCard from './TimelineCard'

/**
 * Timeline Component - Zeigt die Kartenreihe eines Spielers
 * Spieler können neue Karten zwischen bestehende Karten platzieren
 */
function Timeline({ cards = [], onPlaceCard, isMyTurn = false, canPlaceCard = true }) {
  return (
    <div className="w-full overflow-x-auto py-4">
      <div className="flex items-center gap-2 min-w-min px-4">
        {/* Insert-Button ganz links (Position 0) */}
        <PlacementSlot 
          position={0}
          onClick={() => onPlaceCard(0)}
          disabled={!canPlaceCard || !isMyTurn}
          isFirst={true}
        />
        
        {/* Alle Karten mit Insert-Buttons dazwischen */}
        {cards.map((card, idx) => (
          <div key={card.track_id || idx} className="flex items-center gap-2">
            <TimelineCard 
              title={card.title}
              artist={card.artist}
              year={card.year}
            />
            
            {/* Insert-Button nach dieser Karte */}
            <PlacementSlot 
              position={idx + 1}
              onClick={() => onPlaceCard(idx + 1)}
              disabled={!canPlaceCard || !isMyTurn}
            />
          </div>
        ))}
      </div>
      
      {/* Hinweis-Text */}
      {cards.length === 0 && (
        <div className="text-center text-gray-400 py-8">
          <p>Deine Timeline ist noch leer</p>
          <p className="text-sm">Platziere Karten von alt (links) nach neu (rechts)</p>
        </div>
      )}
    </div>
  )
}

/**
 * PlacementSlot - Button zum Platzieren einer neuen Karte
 */
function PlacementSlot({ position, onClick, disabled = false, isFirst = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        flex-shrink-0 w-12 h-32 rounded-lg border-2 border-dashed
        flex items-center justify-center
        transition-all duration-200
        ${disabled 
          ? 'border-gray-700 text-gray-700 cursor-not-allowed' 
          : 'border-hister-pink text-hister-pink hover:bg-hister-pink hover:bg-opacity-10 hover:scale-110 cursor-pointer'
        }
        ${isFirst ? 'border-blue-500 text-blue-500' : ''}
      `}
      title={disabled ? 'Nicht dein Zug' : `Karte hier platzieren (Position ${position})`}
    >
      <Plus className="w-6 h-6" />
    </button>
  )
}

export default Timeline
