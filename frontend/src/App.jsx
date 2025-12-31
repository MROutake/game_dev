import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import CreateLobbyPage from './pages/CreateLobbyPage'
import JoinLobbyPage from './pages/JoinLobbyPage'
import LobbyPage from './pages/LobbyPage'
import GamePage from './pages/GamePage'

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create" element={<CreateLobbyPage />} />
          <Route path="/join" element={<JoinLobbyPage />} />
          <Route path="/lobby/:sessionId" element={<LobbyPage />} />
          <Route path="/game/:sessionId" element={<GamePage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
