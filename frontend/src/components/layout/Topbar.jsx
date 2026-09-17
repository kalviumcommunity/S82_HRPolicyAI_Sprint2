// src/components/layout/Topbar.jsx
import React from 'react';
import { Menu, Globe, CheckCircle2, ShieldCheck, HelpCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export function Topbar({ onMenuClick, title, subtitle }) {
  const { user } = useAuth();
  const isMock = import.meta.env.VITE_USE_MOCK_API !== 'false';

  return (
    <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-20 px-4 sm:px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
          aria-label="Open sidebar navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-base sm:text-lg font-semibold text-slate-900 leading-tight">
            {title || 'HR Policy Assistant'}
          </h1>
          {subtitle && (
            <p className="hidden sm:block text-xs text-slate-500">{subtitle}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2.5 sm:gap-4">
        {/* Jurisdiction / Region Indicator */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-700">
          <Globe className="w-3.5 h-3.5 text-slate-500" />
          <span>Region: {user?.region || 'Global'}</span>
        </div>

        {/* Backend Connectivity Status */}
        <div
          title={
            isMock
              ? 'Using Centralized Mock RAG Engine. Set VITE_USE_MOCK_API=false for FastAPI.'
              : 'Connected to Live FastAPI RAG Backend'
          }
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
            isMock
              ? 'bg-blue-50 text-blue-700 border border-blue-200'
              : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
          }`}
        >
          <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
          <span className="hidden md:inline">{isMock ? 'Mock RAG Mode' : 'FastAPI Connected'}</span>
          <span className="md:hidden">{isMock ? 'Mock' : 'Live'}</span>
        </div>

        {/* Security badge */}
        <div className="hidden lg:flex items-center gap-1 text-slate-400 text-xs" title="SOC2 Type II & GDPR Compliant Internal Knowledge Base">
          <ShieldCheck className="w-4 h-4 text-slate-400" />
          <span>Encrypted</span>
        </div>
      </div>
    </header>
  );
}
