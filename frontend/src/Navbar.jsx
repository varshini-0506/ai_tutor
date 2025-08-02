import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';
import './Navbar.css';

export default function Navbar({ onLogout }) {
  const { user } = useAuth();
  const isLoggedIn = !!user;
  const isTeacher = user?.role === 'teacher';

  return (
    <nav className="navbar">
      <div className="nav-links">
        {isLoggedIn && <Link to="/">Home</Link>}
        
        {isTeacher ? (
          // Teacher navigation
          <>
            <Link to="/students">Students</Link>
            <Link to="/reports">Reports</Link>
            <Link to="/content">Content</Link>
          </>
        ) : (
          // Student navigation
          <>
            <Link to="/content">Content</Link>
            <Link to="/quiz">Quiz</Link>
            <Link to="/ai-tutor">AI Tutor</Link>
            <Link to="/report">Report</Link>
            <Link to="/collaboration">Collaboration</Link>
            <Link to="/calendar">📅 Calendar</Link>
          </>
        )}
      </div>
      
      <div className="nav-user">
        {isLoggedIn && user?.role !== 'common' && <span className="user-role">{user?.role}</span>}
        {isLoggedIn ? (
          <button onClick={onLogout} className="logout-btn">Logout</button>
        ) : null}
      </div>
    </nav>
  );
} 