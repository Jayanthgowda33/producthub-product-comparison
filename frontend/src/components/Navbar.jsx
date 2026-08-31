import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/', label: 'Shop', icon: '◆' },
  { to: '/cart', label: 'Cart', icon: '◇' },
  { to: '/orders', label: 'Orders', icon: '▤' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <aside className="sidebar">
      <Link to="/" className="brand">
        <span className="brand-mark">◈</span> ProductHub
      </Link>

      <nav className="side-links">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`side-link ${location.pathname === link.to ? 'active' : ''}`}
          >
            <span className="side-icon">{link.icon}</span>
            {link.label}
          </Link>
        ))}
      </nav>

      <div className="side-footer">
        {user ? (
          <>
            <div className="side-user">
              <span className="side-user-avatar">{user.username[0].toUpperCase()}</span>
              <div>
                <div className="side-user-name">{user.username}</div>
                <div className="side-user-role">{user.role}</div>
              </div>
            </div>
            <button className="side-logout" onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <div className="side-auth-links">
            <Link to="/login" className="side-link">Log in</Link>
            <Link to="/register" className="side-link accent">Sign up</Link>
          </div>
        )}
      </div>
    </aside>
  )
}