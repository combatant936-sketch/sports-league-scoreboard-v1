import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AdminLayout, PublicLayout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './hooks/useAuth';
import { HomePage } from './pages/HomePage';
import { MatchDetailPage } from './pages/MatchDetailPage';
import { MatchesPage } from './pages/MatchesPage';
import { TeamDetailPage } from './pages/TeamDetailPage';
import { TeamsPage } from './pages/TeamsPage';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { AdminLeaguePage } from './pages/admin/AdminLeaguePage';
import { AdminMatchManagePage } from './pages/admin/AdminMatchManagePage';
import { AdminMatchesPage } from './pages/admin/AdminMatchesPage';
import { AdminPlayersPage } from './pages/admin/AdminPlayersPage';
import { AdminTeamsPage } from './pages/admin/AdminTeamsPage';
import { LoginPage } from './pages/admin/LoginPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<PublicLayout />}>
            <Route index element={<HomePage />} />
            <Route path="teams" element={<TeamsPage />} />
            <Route path="teams/:id" element={<TeamDetailPage />} />
            <Route path="matches" element={<MatchesPage />} />
            <Route path="matches/:id" element={<MatchDetailPage />} />
            <Route path="admin/login" element={<LoginPage />} />
          </Route>

          <Route
            path="admin"
            element={
              <ProtectedRoute>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<AdminDashboard />} />
            <Route path="league" element={<AdminLeaguePage />} />
            <Route path="teams" element={<AdminTeamsPage />} />
            <Route path="players" element={<AdminPlayersPage />} />
            <Route path="matches" element={<AdminMatchesPage />} />
            <Route path="matches/:id" element={<AdminMatchManagePage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
