/**
 * API Service - Backend Communication
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Session Management
export const createSession = async (hostName) => {
  const response = await api.post('/game/session/create', { host_name: hostName })
  return response.data
}

export const addPlayer = async (sessionId, playerName) => {
  const response = await api.post('/game/session/player/add', {
    session_id: sessionId,
    player_name: playerName
  })
  return response.data
}

// Lobby Discovery
export const discoverLobbies = async () => {
  try {
    console.log('🔍 Suche nach Lobbies...')
    const response = await api.get('/game/lobbies')
    console.log('📊 Lobby Response:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ Fehler beim Lobby Discovery:', error)
    console.error('❌ Error details:', error.response?.data)
    return []
  }
}

// Playlist Management
export const loadPlaylist = async (sessionId, playlistId) => {
  const response = await api.post('/game/session/playlist/load', {
    session_id: sessionId,
    playlist_id: playlistId
  })
  return response.data
}

// Game Actions
export const startGame = async (sessionId) => {
  const response = await api.post(`/game/start?session_id=${sessionId}`)
  return response.data
}

export const submitGuess = async (guessData) => {
  const response = await api.post('/game/guess', guessData)
  return response.data
}

export const nextTrack = async (sessionId) => {
  const response = await api.post('/game/next', { session_id: sessionId })
  return response.data
}

export const getLeaderboard = async (sessionId) => {
  const response = await api.get(`/game/leaderboard/${sessionId}`)
  return response.data
}

// Session Players
export const getSessionPlayers = async (sessionId) => {
  const response = await api.get(`/game/session/${sessionId}/players`)
  return response.data
}

export default api
