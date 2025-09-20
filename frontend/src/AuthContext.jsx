import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext(null);

// Helper function to check if token is expired
const isTokenExpired = (token) => {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch (e) {
    console.error('Error parsing token:', e);
    return true;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const token = sessionStorage.getItem('token');
    const role = sessionStorage.getItem('role');
    const username = sessionStorage.getItem('username');
    if (token) {
      // Check if token is expired on initialization
      if (isTokenExpired(token)) {
        console.log('Token is expired on app start - clearing session');
        sessionStorage.clear();
        return null;
      }
      return { token, role, username };
    }
    return null;
  });

  const login = (token, role, username) => {
    sessionStorage.setItem('token', token);
    sessionStorage.setItem('role', role);
    sessionStorage.setItem('username', username);
    setUser({ token, role, username });
  };

  const logout = () => {
    sessionStorage.clear();
    setUser(null);
  };

  // Function to validate current token
  const validateToken = () => {
    const token = sessionStorage.getItem('token');
    if (isTokenExpired(token)) {
      logout();
      return false;
    }
    return true;
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, validateToken, isTokenExpired }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
}; 