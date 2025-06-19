import { Link } from 'react-router-dom';
import './Navbar.css';

export default function Navbar({ role, onLogout, isLoggedIn }) {
  return (
    <nav className="navbar">
      {isLoggedIn && <Link to="/">Home</Link>}
      {isLoggedIn && <Link to="/content">Content</Link>}
      {isLoggedIn && <Link to="/quizzes">Quizzes</Link>}
      {isLoggedIn && <Link to="/ai-tutor">AI Tutor</Link>}
      {isLoggedIn && <Link to="/report">Report</Link>}
      {isLoggedIn && <Link to="/collaboration">Collaboration</Link>}
      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {isLoggedIn && <span style={{ color: '#fff', fontWeight: 'bold' }}>{role}</span>}
        {isLoggedIn ? (
          <button onClick={onLogout} style={{ background: '#dc3545', color: '#fff', border: 'none', borderRadius: 6, padding: '0.4rem 1rem', cursor: 'pointer' }}>Logout</button>
        ) : null}
      </div>
    </nav>
  );
} 