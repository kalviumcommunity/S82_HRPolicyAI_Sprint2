// src/pages/Profile.jsx
import React, { useState } from 'react';
import { User, Mail, Globe, Shield, Briefcase, Calendar, CheckCircle2 } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';

export function Profile() {
  const { user, isAdmin, logout } = useAuth();
  const [selectedRegion, setSelectedRegion] = useState(user?.region || 'India');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSavePreference = (e) => {
    e.preventDefault();
    if (user) {
      user.region = selectedRegion;
      localStorage.setItem('hr_user', JSON.stringify(user));
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    }
  };

  return (
    <PageContainer
      title="Employee Profile & Preferences"
      subtitle="Manage your regional jurisdiction and policy retrieval settings"
    >
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Profile Card Header */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col sm:flex-row items-center sm:items-start gap-5">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-bold text-2xl flex items-center justify-center shadow-md shadow-blue-500/20 shrink-0">
            {user?.avatar || 'EP'}
          </div>

          <div className="text-center sm:text-left flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-1">
              <h2 className="text-xl font-bold text-slate-900">{user?.name || 'Employee Name'}</h2>
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold self-center sm:self-auto ${
                  isAdmin
                    ? 'bg-amber-100 text-amber-800'
                    : 'bg-blue-100 text-blue-800'
                }`}
              >
                {isAdmin ? 'HR Administrator' : 'Standard Employee'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-3">{user?.email}</p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-3 border-t border-slate-100">
              <div>
                <span className="text-slate-400 block">Department</span>
                <span className="font-semibold text-slate-700">{user?.department || 'Engineering'}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Jurisdiction</span>
                <span className="font-semibold text-slate-700">{user?.region || 'India'}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Joined</span>
                <span className="font-semibold text-slate-700">{user?.joinedDate || '2024-03-15'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Regional Policy Setting */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs">
          <h3 className="text-base font-semibold text-slate-900 mb-1">
            Regional Policy Jurisdiction
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            The AI RAG pipeline filters retrieved chunks based on your region to present local statutory rules (such as India leave entitlements vs. USA PTO policies).
          </p>

          <form onSubmit={handleSavePreference} className="space-y-4 max-w-md">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Active Region
              </label>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="w-full text-xs sm:text-sm px-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="India">India (APAC HQ)</option>
                <option value="USA">United States (Americas)</option>
                <option value="UK">United Kingdom (EMEA)</option>
                <option value="Europe">European Union (DACH/Western Europe)</option>
                <option value="Singapore">Singapore (ASEAN)</option>
                <option value="Global">Global / Expatriate Standard</option>
              </select>
            </div>

            <div className="flex items-center gap-3">
              <Button type="submit" variant="primary" size="sm">
                Save Jurisdiction
              </Button>
              {savedSuccess && (
                <span className="text-xs font-medium text-emerald-600 flex items-center gap-1 animate-in fade-in">
                  <CheckCircle2 className="w-4 h-4" /> Preference updated!
                </span>
              )}
            </div>
          </form>
        </div>

        {/* Security / Session Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex items-center justify-between">
          <div>
            <h4 className="text-sm font-semibold text-slate-900">Current Session</h4>
            <p className="text-xs text-slate-500 mt-0.5">
              Signed in with employee single sign-on token.
            </p>
          </div>
          <Button variant="danger" size="sm" onClick={logout}>
            Sign Out
          </Button>
        </div>
      </div>
    </PageContainer>
  );
}
