import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';

export default function Navbar({ onLogout }) {
  const { user } = useAuth();
  const isLoggedIn = !!user;
  const isTeacher = user?.role === 'teacher';

  return (
    <nav style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '1rem 2rem',
      color: 'white',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
    }}>
      <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
        AI Tutor Platform
      </div>
      
      {isLoggedIn && (
        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          {isTeacher ? (
            <>
              <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Home</Link>
              <Link to="/students" style={{ color: 'white', textDecoration: 'none' }}>Students</Link>
              <Link to="/reports" style={{ color: 'white', textDecoration: 'none' }}>Reports</Link>
              <Link to="/content" style={{ color: 'white', textDecoration: 'none' }}>Content</Link>
            </>
          ) : (
            <>
              <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Home</Link>
              <Link to="/lessons" style={{ color: 'white', textDecoration: 'none' }}>Content</Link>
              <Link to="/quizzes" style={{ color: 'white', textDecoration: 'none' }}>Quizzes</Link>
              <Link to="/tutor" style={{ color: 'white', textDecoration: 'none' }}>AI Tutor</Link>
            </>
          )}
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span>Welcome, {user?.username || 'User'}!</span>
            <button
              onClick={onLogout}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      )}
    </nav>
  );
} 