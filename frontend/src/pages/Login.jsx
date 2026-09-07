// src/pages/Login.jsx
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Mail, Lock, AlertCircle, ArrowRight, Shield, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common/Button';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/chat';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!email.trim() || !password) {
      setFormError('Please enter both email and password.');
      return;
    }

    try {
      setLoading(true);
      const user = await login(email.trim(), password);
      // If admin and default landing, direct to /admin
      if (user.role === 'HR_ADMIN' && from === '/chat') {
        navigate('/admin');
      } else {
        navigate(from, { replace: true });
      }
    } catch (err) {
      setFormError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  // 1-Click quick fill for seamless evaluator testing
  const handleQuickFill = (type) => {
    if (type === 'EMPLOYEE') {
      setEmail('sarah.jenkins@company.com');
      setPassword('password123');
    } else {
      setEmail('david.miller@company.com');
      setPassword('admin123');
    }
    setFormError('');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 text-white shadow-md shadow-blue-500/20 mb-3">
          <Sparkles className="w-6 h-6" />
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          Sign in to HRPolicyAI
        </h2>
        <p className="mt-1.5 text-sm text-slate-500">
          Internal Enterprise Policy Knowledge & Compliance Assistant
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-8 px-6 shadow-sm border border-slate-200 sm:rounded-2xl sm:px-10">
          {formError && (
            <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{formError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Company Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  required
                  className="w-full text-xs sm:text-sm pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-700">Password</label>
                <span className="text-[11px] text-slate-400">Default: password123</span>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full text-xs sm:text-sm pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                size="md"
                className="w-full"
                isLoading={loading}
              >
                Sign In
              </Button>
            </div>
          </form>

          {/* Quick Demo Credentials Box */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 text-center mb-2.5">
              Quick 1-Click Demo Accounts
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickFill('EMPLOYEE')}
                className="p-2 border border-slate-200 hover:border-blue-400 hover:bg-blue-50/50 rounded-lg text-left transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                  <User className="w-3.5 h-3.5 text-blue-600" />
                  <span>Employee</span>
                </div>
                <p className="text-[10px] text-slate-500 truncate mt-0.5">Sarah Jenkins</p>
              </button>

              <button
                type="button"
                onClick={() => handleQuickFill('HR_ADMIN')}
                className="p-2 border border-slate-200 hover:border-amber-400 hover:bg-amber-50/50 rounded-lg text-left transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                  <Shield className="w-3.5 h-3.5 text-amber-600" />
                  <span>HR Admin</span>
                </div>
                <p className="text-[10px] text-slate-500 truncate mt-0.5">David Miller</p>
              </button>
            </div>
          </div>

          <div className="mt-5 text-center text-xs text-slate-500">
            Don't have an employee account?{' '}
            <Link to="/register" className="font-semibold text-blue-600 hover:text-blue-700">
              Register here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
