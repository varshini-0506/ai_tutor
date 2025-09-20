import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, Link } from 'react-router-dom';

import Navbar from './Navbar';
import Home from './Home';
import ContentList from './ContentList';
import QuizList from './QuizList';
import Quiz from './Quiz';
import Report from './Report';
import Collaboration from './Collaboration';
import Login from './Login';
import AiTutorChat from './AiTutorChat';
import Calendar from './Calendar';

import Lessons from './components/Lessons';
import StudentManagement from './components/StudentManagement';
import ContentManagement from './components/ContentManagement';
// QuizManagement and ClassManagement are no longer routed
// import QuizManagement from './components/QuizManagement';
// import ClassManagement from './components/ClassManagement';

import './App.css';
import { AuthProvider, useAuth } from './AuthContext.jsx';

// 🔹 Inner component to handle routing after login
function AppRoutes() {
  const { user, login, logout, validateToken } = useAuth();
  const navigate = useNavigate();
  const isTeacher = user?.role === 'teacher';

  // Validate token on component mount and route changes
  useEffect(() => {
    if (user && !validateToken()) {
      console.log('Token validation failed - redirecting to login');
      navigate('/login');
    }
  }, [user, validateToken, navigate]);

  const handleLogin = (token, role, username) => {
    login(token, role, username);
    navigate('/');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Navbar only if logged in */}
      {!!user && <Navbar onLogout={handleLogout} isLoggedIn={!!user} />}

      {/* Removed static nav for lessons/analytics */}

      <Routes>
        {!user ? (
          <Route path="*" element={<Login onLogin={handleLogin} />} />
        ) : (
          <>
            <Route path="/" element={<Home />} />
            
            {/* Student-specific routes */}
            {!isTeacher && (
              <>
                <Route path="/content" element={<Lessons />} />
                <Route path="/quiz" element={<Quiz token={sessionStorage.getItem('token')} />} />
                <Route path="/ai-tutor" element={<AiTutorChat token={sessionStorage.getItem('token')} />} />
                <Route path="/report" element={<Report />} />           
                <Route path="/collaboration" element={<Collaboration token={sessionStorage.getItem('token')} role={user?.role} />} />
                <Route path="/calendar" element={<Calendar />} />
              </>
            )}
            
            {/* Teacher-specific routes */}
            {isTeacher && (
              <>
                <Route path="/students" element={<StudentManagement />} />
                <Route path="/reports" element={<Report />} />
                <Route path="/content" element={<ContentManagement />} />
              </>
            )}
            
            {/* Fallback for any other route */}
            <Route path="*" element={<Navigate to="/" />} />
          </>
        )}
      </Routes>
    </>
  );
}

// 🔹 Main wrapper
function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
