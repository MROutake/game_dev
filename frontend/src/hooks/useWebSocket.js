/**
 * WebSocket Hook for Real-time Updates
 */
import { useEffect, useRef, useState } from 'react'
import { io } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000'

export function useWebSocket(sessionId, handlers = {}) {
  const [connected, setConnected] = useState(false)
  const socketRef = useRef(null)

  useEffect(() => {
    if (!sessionId) return

    // Socket.IO Connection
    const socket = io(SOCKET_URL, {
      transports: ['websocket'],
      query: { sessionId }
    })

    socketRef.current = socket

    // Connection Events
    socket.on('connect', () => {
      console.log('✅ WebSocket verbunden')
      setConnected(true)
      socket.emit('join_lobby', { session_id: sessionId })
    })

    socket.on('disconnect', () => {
      console.log('❌ WebSocket getrennt')
      setConnected(false)
    })

    // Game Events
    socket.on('player_joined', (data) => {
      console.log('👤 Spieler beigetreten:', data)
      handlers.onPlayerJoined?.(data)
    })

    socket.on('player_left', (data) => {
      console.log('👋 Spieler verlassen:', data)
      handlers.onPlayerLeft?.(data.player_id)
    })

    socket.on('game_started', (data) => {
      console.log('🎮 Spiel gestartet:', data)
      handlers.onGameStarted?.(data)
    })

    socket.on('session_closed', (data) => {
      console.log('🚪 Session geschlossen:', data)
      handlers.onSessionClosed?.(data)
    })

    socket.on('new_track', (data) => {
      console.log('🎵 Neuer Track:', data)
      handlers.onNewTrack?.(data)
    })

    socket.on('guess_result', (data) => {
      console.log('✅ Guess-Ergebnis:', data)
      handlers.onGuessResult?.(data)
    })

    socket.on('leaderboard_update', (data) => {
      console.log('🏆 Leaderboard Update:', data)
      handlers.onLeaderboardUpdate?.(data)
    })

    // Cleanup
    return () => {
      console.log('🔌 WebSocket schließen')
      socket.disconnect()
    }
  }, [sessionId])

  const sendMessage = (data) => {
    if (socketRef.current && connected) {
      socketRef.current.emit('message', data)
    }
  }

  return { connected, sendMessage, socket: socketRef.current }
}
