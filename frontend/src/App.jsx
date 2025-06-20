import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import Home from './Home';
import ContentList from './ContentList';
import QuizList from './QuizList';
import Report from './Report';
import Collaboration from './Collaboration';
import Login from './Login';
import AiTutorChat from './AiTutorChat';
import './App.css';

function AppRoutes({ token, setToken, role, setRole, handleLogout }) {
  const navigate = useNavigate();

  const handleLogin = (jwt, userRole) => {
    setToken(jwt);
    setRole(userRole);
    navigate('/');
  };

  return (
    <>
      {/* Only show Navbar when logged in */}
      {!!token && <Navbar role={role} onLogout={handleLogout} isLoggedIn={!!token} />}
      <Routes>
        {!token ? (
          <Route path="*" element={<Login onLogin={handleLogin} />} />
        ) : (
          <>
            <Route path="/" element={<Home />} />
            <Route path="/content" element={<ContentList token={token} role={role} />} />
            <Route path="/quizzes" element={<QuizList token={token} role={role} />} />
            <Route path="/ai-tutor" element={<AiTutorChat token={token} />} />
            <Route path="/report" element={<Report />} />
            <Route path="/collaboration" element={<Collaboration />} />
            <Route path="*" element={<Navigate to="/" />} />
          </>
        )}
      </Routes>
    </>
  );
}

function App() {
  const [token, setToken] = useState(null);
  const [role, setRole] = useState(null);

  const handleLogout = () => {
    setToken(null);
    setRole(null);
  };

  return (
    <Router>
      <AppRoutes token={token} setToken={setToken} role={role} setRole={setRole} handleLogout={handleLogout} />
    </Router>
  );
}

export default App;
