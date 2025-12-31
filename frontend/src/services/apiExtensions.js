/**
 * Zusätzliche API Calls
 */
import api from './api'

// Hole Spieler einer Session
export const getSessionPlayers = async (sessionId) => {
  const response = await api.get(`/game/session/${sessionId}/players`)
  return response.data
}

export { api as default }
