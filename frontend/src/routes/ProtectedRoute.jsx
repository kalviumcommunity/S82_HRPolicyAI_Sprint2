// src/routes/ProtectedRoute.jsx
import React, { useState } from 'react';
import { Navigate, useLocation, Link } from 'react-router-dom';
import { ShieldAlert, KeyRound, Lock, ArrowLeft, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Loading } from '../components/common/Loading';
import { Button } from '../components/common/Button';

export function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, user, loading, unlockAdmin } = useAuth();
  const location = useLocation();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loading message="Authenticating session..." size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If route requires HR_ADMIN and user is only EMPLOYEE, show the Admin Password Prompt
  if (requiredRole === 'HR_ADMIN' && user?.role !== 'HR_ADMIN') {
    const handleAdminUnlock = (e) => {
      e.preventDefault();
      setError('');
      try {
        setSubmitting(true);
        unlockAdmin(password);
      } catch (err) {
        setError(err.message || 'Incorrect admin password.');
      } finally {
        setSubmitting(false);
      }
    };

    return (
      <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-amber-600 text-white shadow-md shadow-amber-500/20 mb-3">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">
            Admin Portal Locked
          </h2>
          <p className="mt-1.5 text-xs text-slate-500">
            Enter the HR Administrator password to access this management area
          </p>
        </div>

        <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
          <div className="bg-white py-8 px-6 shadow-sm border border-slate-200 sm:rounded-2xl sm:px-10">
            {error && (
              <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleAdminUnlock} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Admin Password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter admin password"
                    autoFocus
                    required
                    className="w-full text-xs sm:text-sm pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                  />
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="md"
                className="w-full bg-amber-600 hover:bg-amber-700 text-white"
                isLoading={submitting}
                icon={KeyRound}
              >
                Unlock Admin Portal
              </Button>
            </form>

            <div className="mt-5 text-center">
              <Link
                to="/chat"
                className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Employee Assistant</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return children;
}

