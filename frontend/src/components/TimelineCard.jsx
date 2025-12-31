import { Music2, Calendar } from 'lucide-react'

/**
 * TimelineCard - Einzelne Karte in der Timeline
 * Zeigt Titel, Künstler und Jahr
 */
function TimelineCard({ title, artist, year, isRevealed = true }) {
  return (
    <div className="flex-shrink-0 w-40 h-32 card p-3 hover:scale-105 transition-transform">
      {/* Jahr (oben) */}
      <div className="flex items-center justify-center mb-2">
        <Calendar className="w-4 h-4 mr-1 text-hister-pink" />
        <span className="text-lg font-bold text-hister-pink">
          {isRevealed ? year : '????'}
        </span>
      </div>
      
      {/* Titel */}
      <div className="text-sm font-semibold text-white truncate mb-1" title={title}>
        {title}
      </div>
      
      {/* Künstler */}
      <div className="flex items-center text-xs text-gray-400 truncate" title={artist}>
        <Music2 className="w-3 h-3 mr-1" />
        {artist}
      </div>
    </div>
  )
}

export default TimelineCard
