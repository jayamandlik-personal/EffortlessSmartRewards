import { Link, useLocation } from 'react-router-dom'
import { Home, CreditCard, Gift, Settings } from 'lucide-react'
import './Sidebar.css'

const Sidebar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/transactions', label: 'Transactions', icon: CreditCard },
    { path: '/rewards', label: 'Rewards', icon: Gift },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-text">Effortless</span>
        </div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}

export default Sidebar

