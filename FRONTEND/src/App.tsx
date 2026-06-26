// Main App Component with Routing and Redux Provider
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from './redux/store';
import { setUser } from './redux/slices/authSlice';
import { isAuthenticated } from './services/authService';

// Layout & Pages
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import SchemesPage from './pages/Welfare/SchemesPage';
import WelfareChatPage from './pages/Welfare/ChatPage';
import JobsPage from './pages/Internships/JobsPage';
import InternshipChatPage from './pages/Internships/ChatPage';
import CoachPage from './pages/Interview/CoachPage';
import DocumentsPage from './pages/DigiLocker/DocumentsPage';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import NotFoundPage from './pages/Auth/NotFoundPage';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  
  if (!isLoggedIn && !isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Public Route Component (redirects to dashboard if already logged in)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  
  if (isLoggedIn || isAuthenticated()) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

export const App: React.FC = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    // Remove the mock user 'Alex Mercer' and force login initially
    if (isAuthenticated()) {
      localStorage.removeItem('token');
    }
  }, [dispatch]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Auth routes */}
        <Route path="/login" element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        } />

        {/* Protected app routes inside MainLayout */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="welfare" element={<SchemesPage />} />
          <Route path="welfare/chat" element={<WelfareChatPage />} />
          <Route path="internships" element={<JobsPage />} />
          <Route path="internships/chat" element={<InternshipChatPage />} />
          <Route path="interview" element={<CoachPage />} />
          <Route path="digilocker" element={<DocumentsPage />} />
        </Route>

        {/* 404 Route */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
