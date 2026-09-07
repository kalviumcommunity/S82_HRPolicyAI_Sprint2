// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize from localStorage or fallback to default demo user for seamless preview
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('hr_user');
      const storedToken = localStorage.getItem('hr_token');

      if (storedUser && storedToken) {
        setUser(JSON.parse(storedUser));
        setToken(storedToken);
      } else {
        // Automatically start with a logged-in demo employee for instant productivity
        const defaultDemo = {
          id: 'usr_emp_01',
          name: 'Sarah Jenkins',
          email: 'sarah.jenkins@company.com',
          role: 'EMPLOYEE',
          region: 'India',
          department: 'Engineering',
          avatar: 'SJ',
          joinedDate: '2024-03-15',
        };
        const demoToken = 'mock_jwt_token_demo';
        setUser(defaultDemo);
        setToken(demoToken);
        localStorage.setItem('hr_user', JSON.stringify(defaultDemo));
        localStorage.setItem('hr_token', demoToken);
      }
    } catch (err) {
      console.error('Error hydrating auth state:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      const response = await api.auth.login({ email, password });
      setUser(response.user);
      setToken(response.token);
      localStorage.setItem('hr_user', JSON.stringify(response.user));
      localStorage.setItem('hr_token', response.token);
      return response.user;
    } catch (err) {
      setError(err.message || 'Login failed.');
      throw err;
    }
  }, []);

  const register = useCallback(async ({ name, email, password, region }) => {
    setError(null);
    try {
      const response = await api.auth.register({ name, email, password, region });
      setUser(response.user);
      setToken(response.token);
      localStorage.setItem('hr_user', JSON.stringify(response.user));
      localStorage.setItem('hr_token', response.token);
      return response.user;
    } catch (err) {
      setError(err.message || 'Registration failed.');
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    setError(null);
    localStorage.removeItem('hr_user');
    localStorage.removeItem('hr_token');
  }, []);

  // Switch role quickly (useful for demo & testing between Employee and HR Admin)
  const switchDemoRole = useCallback((newRole) => {
    if (newRole === 'HR_ADMIN') {
      const adminUser = {
        id: 'usr_adm_01',
        name: 'David Miller',
        email: 'david.miller@company.com',
        role: 'HR_ADMIN',
        region: 'India',
        department: 'People Operations',
        avatar: 'DM',
        joinedDate: '2022-06-01',
      };
      setUser(adminUser);
      localStorage.setItem('hr_user', JSON.stringify(adminUser));
    } else {
      const empUser = {
        id: 'usr_emp_01',
        name: 'Sarah Jenkins',
        email: 'sarah.jenkins@company.com',
        role: 'EMPLOYEE',
        region: 'India',
        department: 'Engineering',
        avatar: 'SJ',
        joinedDate: '2024-03-15',
      };
      setUser(empUser);
      localStorage.setItem('hr_user', JSON.stringify(empUser));
    }
  }, []);

  const value = {
    user,
    token,
    role: user?.role || null,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'HR_ADMIN',
    loading,
    error,
    login,
    register,
    logout,
    switchDemoRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
