import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';

export default function Navbar({ onLogout }) {
  const { user } = useAuth();
  const isLoggedIn = !!user;
  const isTeacher = user?.role === 'teacher';

  return (
    <nav style={{
      background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
      padding: '1rem 2rem',
      color: 'white',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
    }}>
      {isLoggedIn && (
        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          {isTeacher ? (
            <>
              <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Home</Link>
              <Link to="/students" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Students</Link>
              <Link to="/reports" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Reports</Link>
              <Link to="/content" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Content</Link>
            </>
          ) : (
            <>
              <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Home</Link>
              <Link to="/lessons" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Content</Link>
              <Link to="/quizzes" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Quizzes</Link>
              <Link to="/tutor" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>AI Tutor</Link>
              <Link to="/report" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Reports</Link>
              <Link to="/collaboration" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Collaborations</Link>
            </>
          )}
          
          <button
            onClick={onLogout}
            style={{
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
} 