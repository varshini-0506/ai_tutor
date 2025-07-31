import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';

export default function Navbar({ onLogout }) {
  const { user } = useAuth();
  const isLoggedIn = !!user;
  const isTeacher = user?.role === 'teacher';

  return (
    <nav className="navbar" style={{
      background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
      padding: '1rem 2rem',
      color: 'white',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
    }}>
      <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
        {isLoggedIn && <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Home</Link>}
        
        {isTeacher ? (
          // Teacher navigation
          <>
            <Link to="/students" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Students</Link>
            <Link to="/reports" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Reports</Link>
            <Link to="/content" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Content</Link>
          </>
        ) : (
          // Student navigation
          <>
            <Link to="/content" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Content</Link>
            <Link to="/quiz" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Quiz</Link>
            <Link to="/ai-tutor" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>AI Tutor</Link>
            <Link to="/report" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Report</Link>
            <Link to="/collaboration" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Collaboration</Link>
          </>
        )}
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {isLoggedIn && user?.role !== 'common' && <span style={{ color: '#fff', fontWeight: 'bold' }}>{user?.role}</span>}
        {isLoggedIn ? (
          <button onClick={onLogout} style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', padding: '0.5rem 1rem', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}>Logout</button>
        ) : null}
      </div>
    </nav>
  );
} 