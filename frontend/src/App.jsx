import { useState } from 'react';
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

import Lessons from './components/Lessons';
import Analytics from './components/Analytics';

import './App.css';

// 🔹 Inner component to handle routing after login
function AppRoutes({ token, setToken, role, setRole, handleLogout }) {
  const navigate = useNavigate();

  const handleLogin = (jwt, userRole, username) => {
    setToken(jwt);
    setRole(userRole);
    localStorage.setItem('username', username);
    navigate('/');
  };

  return (
    <>
      {/* Navbar only if logged in */}
      {!!token && <Navbar role={role} onLogout={handleLogout} isLoggedIn={!!token} />}

      {/* Removed static nav for lessons/analytics */}

      <Routes>
        {!token ? (
          <Route path="*" element={<Login onLogin={handleLogin} />} />
        ) : (
          <>
            <Route path="/" element={<Home />} />
            <Route path="/content" element={<Lessons />} />
            <Route path="/quizzes" element={<QuizList token={token} role={role} />} />
            <Route path="/quiz" element={<Quiz token={token} />} />
            <Route path="/ai-tutor" element={<AiTutorChat token={token} />} />
            <Route path="/report" element={<Report />} />
            <Route path="/collaboration" element={<Collaboration token={token} role={role} />} />
            {/* Analytics route can remain if needed */}
            <Route path="/analytics" element={<Analytics />} />
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
  const [token, setToken] = useState(null);
  const [role, setRole] = useState(null);

  const handleLogout = () => {
    setToken(null);
    setRole(null);
    localStorage.removeItem('username');
  };

  return (
    <Router>
      <AppRoutes
        token={token}
        setToken={setToken}
        role={role}
        setRole={setRole}
        handleLogout={handleLogout}
      />
    </Router>
  );
}

export default App;
