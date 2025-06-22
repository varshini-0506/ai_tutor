import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, Link } from 'react-router-dom';

import Navbar from './Navbar';
import Home from './Home';
import ContentList from './ContentList';
import QuizList from './QuizList';
import Report from './Report';
import Collaboration from './Collaboration';
import Login from './Login';
import AiTutorChat from './AiTutorChat';

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
  const { user, login } = useAuth();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const isTeacher = user?.role === 'teacher';

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
                <Route path="/lessons" element={<Lessons />} />
                <Route path="/quizzes" element={<QuizList token={user} role={user} />} />
                <Route path="/tutor" element={<AiTutorChat token={user} />} />
                <Route path="/collaboration" element={<Collaboration />} />
                <Route path="/report" element={<Report />} />
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
            
            {/* Catch-all */}
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
