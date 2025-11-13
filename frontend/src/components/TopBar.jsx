import { Bell, User } from 'lucide-react'
import './TopBar.css'

const TopBar = ({ user }) => {
  return (
    <header className="topbar">
      <div className="topbar-content">
        <div className="topbar-spacer"></div>
        <div className="topbar-actions">
          <button className="icon-button">
            <Bell size={20} />
          </button>
          <div className="user-avatar">
            {user ? (
              <div className="avatar-initials">
                {user.name
                  .split(' ')
                  .map(n => n[0])
                  .join('')
                  .toUpperCase()}
              </div>
            ) : (
              <User size={20} />
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default TopBar

