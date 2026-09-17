// src/components/admin/AdminPasswordModal.jsx
import React, { useState } from 'react';
import { Lock, ShieldAlert, KeyRound, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useAuth } from '../../context/AuthContext';

export function AdminPasswordModal({ isOpen, onClose, onSuccess }) {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { unlockAdmin } = useAuth();

  const handleUnlock = (e) => {
    e?.preventDefault();
    setError('');

    if (!password) {
      setError('Please enter the admin password.');
      return;
    }

    try {
      setLoading(true);
      unlockAdmin(password);
      setPassword('');
      setError('');
      if (onSuccess) onSuccess();
      if (onClose) onClose();
    } catch (err) {
      setError(err.message || 'Incorrect admin password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        setPassword('');
        setError('');
        if (onClose) onClose();
      }}
      title="Admin Portal Security Access"
      subtitle="Restricted to authorized People Operations administrators"
      maxWidth="max-w-md"
      footer={
        <>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setPassword('');
              setError('');
              if (onClose) onClose();
            }}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleUnlock}
            isLoading={loading}
            icon={KeyRound}
          >
            Unlock Admin Portal
          </Button>
        </>
      }
    >
      <form onSubmit={handleUnlock} className="space-y-4 py-1">
        <div className="flex items-center gap-3 p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-900">
          <ShieldAlert className="w-6 h-6 text-amber-600 shrink-0" />
          <div className="text-xs">
            <p className="font-semibold">HR Administrator Credentials Required</p>
            <p className="text-amber-700 mt-0.5">
              Enter the admin password to view and manage policy documents and system analytics.
            </p>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Admin Password
          </label>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <Lock className="w-4 h-4" />
            </div>
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter admin password"
              autoFocus
              required
              className="w-full text-xs sm:text-sm pl-9 pr-10 py-2.5 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 cursor-pointer"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </form>
    </Modal>
  );
}
