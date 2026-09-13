import { Link, NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function PublicLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="site-header">
        <Link to="/" className="brand">
          <span className="brand-icon">🏆</span>
          <span>League Scoreboard</span>
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
        Football League Scoreboard — mock data mode
      </footer>
    </div>
  );
}

export function AdminLayout() {
  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <Link to="/" className="brand compact">
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
