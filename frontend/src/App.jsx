import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Rewards from './pages/Rewards'
import Settings from './pages/Settings'
import './App.css'

// Mock authentication - in production, use proper auth
const MOCK_USER_ID = 1

function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Fetch user data
    fetch(`/api/users/${MOCK_USER_ID}`)
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(err => console.error('Error fetching user:', err))
  }, [])

  return (
    <Router>
      <div className="app">
        <Sidebar />
        <div className="app-main">
          <TopBar user={user} />
          <div className="app-content">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard userId={MOCK_USER_ID} />} />
              <Route path="/transactions" element={<Transactions userId={MOCK_USER_ID} />} />
              <Route path="/rewards" element={<Rewards userId={MOCK_USER_ID} />} />
              <Route path="/settings" element={<Settings userId={MOCK_USER_ID} />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  )
}

export default App

