import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';
import './Login.css';

// Loader component
const Loader = () => (
  <div className="loader">
    <div className="spinner"></div>
  </div>
);

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('student');
  const [error, setError] = useState('');
  const [showSignUp, setShowSignUp] = useState(false);
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSignUpLoading, setIsSignUpLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async e => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      console.log('Attempting login with:', { username, password });
      
      const res = await fetch('https://ai-tutor-backend-m4rr.onrender.com/api/auth/login', {
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
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async e => {
    e.preventDefault();
    setIsSignUpLoading(true);
    setError('');
    setSuccess('');
    
    try {
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      
      const res = await fetch('https://ai-tutor-backend-m4rr.onrender.com/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role })
      });
      
      if (res.ok) {
        // Auto-login after successful registration
        const loginRes = await fetch('https://ai-tutor-backend-m4rr.onrender.com/api/auth/login', {
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
    } catch (error) {
      console.error('Signup error:', error);
      setError('Network error. Please try again.');
    } finally {
      setIsSignUpLoading(false);
    }
  };

  return (
    <div className="login-container">
      {showSignUp ? (
        <form onSubmit={handleSignUp} className="login-form">
          <h2>Sign Up</h2>
          <div className="form-group">
            <input 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              placeholder="Username" 
              required 
              disabled={isSignUpLoading}
            />
          </div>
          <div className="form-group">
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              placeholder="Password" 
              required 
              disabled={isSignUpLoading}
            />
          </div>
          <div className="form-group">
            <input 
              type="password" 
              value={confirmPassword} 
              onChange={e => setConfirmPassword(e.target.value)} 
              placeholder="Confirm Password" 
              required 
              disabled={isSignUpLoading}
            />
          </div>
          <div className="form-group">
            <select 
              value={role} 
              onChange={e => setRole(e.target.value)}
              disabled={isSignUpLoading}
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
              <option value="common">Common</option>
            </select>
          </div>
          <button 
            type="submit" 
            className="btn-primary" 
            disabled={isSignUpLoading}
          >
            {isSignUpLoading ? <Loader /> : 'Sign Up'}
          </button>
          <button 
            type="button" 
            onClick={() => { setShowSignUp(false); setError(''); setSuccess(''); setConfirmPassword(''); }} 
            className="btn-secondary"
            disabled={isSignUpLoading}
          >
            Back to Login
          </button>
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
        </form>
      ) : (
        <form onSubmit={handleSubmit} className="login-form">
          <h2>Login</h2>
          <div className="form-group">
            <input 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              placeholder="Username" 
              required 
              disabled={isLoading}
            />
          </div>
          <div className="form-group">
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              placeholder="Password" 
              required 
              disabled={isLoading}
            />
          </div>
          <div className="form-group">
            <select 
              value={role} 
              onChange={e => setRole(e.target.value)}
              disabled={isLoading}
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
              <option value="common">Common</option>
            </select>
          </div>
          <button 
            type="submit" 
            className="btn-primary" 
            disabled={isLoading}
          >
            {isLoading ? <Loader /> : 'Login'}
          </button>
          <button 
            type="button" 
            onClick={() => { setShowSignUp(true); setError(''); setSuccess(''); setConfirmPassword(''); }} 
            className="btn-secondary"
            disabled={isLoading}
          >
            Sign Up
          </button>
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
        </form>
      )}
    </div>
  );
} 