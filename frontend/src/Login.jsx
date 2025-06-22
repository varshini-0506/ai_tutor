import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('student');
  const [error, setError] = useState('');
  const [showSignUp, setShowSignUp] = useState(false);
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async e => {
    e.preventDefault();
    console.log('Attempting login with:', { username, password });
    
    const res = await fetch('http://127.0.0.1:5000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    console.log('Login response status:', res.status);
    
    if (res.ok) {
      const data = await res.json();
      console.log('Login response data:', data);
      console.log('Access token:', data.access_token);
      console.log('Token length:', data.access_token ? data.access_token.length : 0);
      
      // Store username in sessionStorage for the Report component
      sessionStorage.setItem('username', username);
      
      onLogin(data.access_token, data.role, username);
      navigate('/');
    } else {
      const errorData = await res.json();
      console.error('Login error:', errorData);
      setError(errorData.msg || 'Invalid credentials');
    }
  };

  const handleSignUp = async e => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    const res = await fetch('http://127.0.0.1:5000/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role })
    });
    if (res.ok) {
      // Auto-login after successful registration
      const loginRes = await fetch('http://127.0.0.1:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (loginRes.ok) {
        const data = await loginRes.json();
        // Store username in sessionStorage for the Report component
        sessionStorage.setItem('username', username);
        onLogin(data.access_token, data.role, username);
        navigate('/');
      } else {
        setSuccess('Registration successful! Please log in.');
        setShowSignUp(false);
        setUsername(username);
        setPassword(password);
        setRole(role);
      }
    } else {
      const data = await res.json();
      setError(data.msg || 'Registration failed');
    }
  };

  return (
    <div>
      {showSignUp ? (
        <form onSubmit={handleSignUp} style={{maxWidth: 350, margin: '2rem auto', background: '#fff', padding: '2rem', borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.08)'}}>
          <h2>Sign Up</h2>
          <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" required style={{width: '100%', marginBottom: 12, padding: 8}} />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required style={{width: '100%', marginBottom: 12, padding: 8}} />
          <input type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="Confirm Password" required style={{width: '100%', marginBottom: 12, padding: 8}} />
          <select value={role} onChange={e => setRole(e.target.value)} style={{width: '100%', marginBottom: 12, padding: 8}}>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
            <option value="common">Common</option>
          </select>
          <button type="submit" style={{width: '100%', background: '#28a745', color: '#fff', border: 'none', borderRadius: 6, padding: 10, fontSize: 16, cursor: 'pointer'}}>Sign Up</button>
          <button type="button" onClick={() => { setShowSignUp(false); setError(''); setSuccess(''); setConfirmPassword(''); }} style={{width: '100%', marginTop: 8, background: '#007bff', color: '#fff', border: 'none', borderRadius: 6, padding: 10, fontSize: 16, cursor: 'pointer'}}>Back to Login</button>
          {error && <div style={{color: 'red', marginTop: 10}}>{error}</div>}
          {success && <div style={{color: 'green', marginTop: 10}}>{success}</div>}
        </form>
      ) : (
        <form onSubmit={handleSubmit} style={{maxWidth: 350, margin: '2rem auto', background: '#fff', padding: '2rem', borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.08)'}}>
          <h2>Login</h2>
          <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" required style={{width: '100%', marginBottom: 12, padding: 8}} />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required style={{width: '100%', marginBottom: 12, padding: 8}} />
          <select value={role} onChange={e => setRole(e.target.value)} style={{width: '100%', marginBottom: 12, padding: 8}}>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
            <option value="common">Common</option>
          </select>
          <button type="submit" style={{width: '100%', background: '#007bff', color: '#fff', border: 'none', borderRadius: 6, padding: 10, fontSize: 16, cursor: 'pointer'}}>Login</button>
          <button type="button" onClick={() => { setShowSignUp(true); setError(''); setSuccess(''); setConfirmPassword(''); }} style={{width: '100%', marginTop: 8, background: '#28a745', color: '#fff', border: 'none', borderRadius: 6, padding: 10, fontSize: 16, cursor: 'pointer'}}>Sign Up</button>
          {error && <div style={{color: 'red', marginTop: 10}}>{error}</div>}
          {success && <div style={{color: 'green', marginTop: 10}}>{success}</div>}
        </form>
      )}
    </div>
  );
} 