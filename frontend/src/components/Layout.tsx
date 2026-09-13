import { Link, NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function PublicLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="site-header">
        <Link to="/" className="brand">
          <span className="brand-icon">⚡</span>
          <span>KickPulse</span>
        </Link>
        <nav className="main-nav">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/teams">Teams</NavLink>
          <NavLink to="/matches">Matches</NavLink>
          {user ? (
            <>
              <NavLink to="/admin">Admin</NavLink>
              <button type="button" className="btn-link" onClick={() => logout()}>
                Logout
              </button>
            </>
          ) : (
            <NavLink to="/admin/login">Admin Login</NavLink>
          )}
        </nav>
      </header>
      <main className="site-main">
        <Outlet />
      </main>
      <footer className="site-footer">
        KickPulse — Live Sports League Scoreboard
      </footer>
    </div>
  );
}

export function AdminLayout() {
  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div style={{ marginBottom: '1.25rem' }}>
          <Link to="/admin" className="brand" style={{ textDecoration: 'none' }}>
            <span className="brand-icon">⚡</span>
            <span>KickPulse</span>
          </Link>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: '0.2rem' }}>
            Admin Portal
          </div>
        </div>
        <Link to="/" className="brand compact" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          ← Public site
        </Link>
        <nav className="admin-nav">
          <NavLink to="/admin" end>Dashboard</NavLink>
          <NavLink to="/admin/league">League</NavLink>
          <NavLink to="/admin/teams">Teams</NavLink>
          <NavLink to="/admin/players">Players</NavLink>
          <NavLink to="/admin/matches">Matches</NavLink>
        </nav>
      </aside>
      <div className="admin-content">
        <Outlet />
      </div>
    </div>
  );
}
