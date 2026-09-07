// src/components/layout/Sidebar.jsx
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Clock,
  User,
  Shield,
  FileText,
  LogOut,
  Sparkles,
  Layers,
  ChevronRight,
  RefreshCw,
  X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export function Sidebar({ mobileOpen, setMobileOpen }) {
  const { user, isAdmin, logout, switchDemoRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItemClass = ({ isActive }) =>
    `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
      isActive
        ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
    }`;

  const closeMobile = () => {
    if (setMobileOpen) setMobileOpen(false);
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white border-r border-slate-200 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-slate-900 text-base tracking-tight">HRPolicyAI</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-700">
                v2.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Enterprise Policy RAG</p>
          </div>
        </div>
        {mobileOpen && (
          <button
            type="button"
            onClick={closeMobile}
            className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {/* Workspace section */}
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Employee Workspace
          </p>
          <nav className="space-y-1">
            <NavLink to="/chat" className={navItemClass} onClick={closeMobile}>
              <MessageSquare className="w-4 h-4 shrink-0" />
              <span>HR Assistant</span>
            </NavLink>
            <NavLink to="/history" className={navItemClass} onClick={closeMobile}>
              <Clock className="w-4 h-4 shrink-0" />
              <span>Conversation History</span>
            </NavLink>
            <NavLink to="/profile" className={navItemClass} onClick={closeMobile}>
              <User className="w-4 h-4 shrink-0" />
              <span>My Profile</span>
            </NavLink>
          </nav>
        </div>

        {/* HR Admin Section */}
        {isAdmin && (
          <div>
            <div className="flex items-center justify-between px-3 mb-2">
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                HR Administration
              </p>
              <span className="text-[10px] bg-amber-100 text-amber-800 font-semibold px-1.5 py-0.2 rounded">
                Admin
              </span>
            </div>
            <nav className="space-y-1">
              <NavLink to="/admin" end className={navItemClass} onClick={closeMobile}>
                <Shield className="w-4 h-4 shrink-0 text-amber-600" />
                <span>Admin Dashboard</span>
              </NavLink>
              <NavLink to="/admin/documents" className={navItemClass} onClick={closeMobile}>
                <FileText className="w-4 h-4 shrink-0 text-amber-600" />
                <span>Policy Documents</span>
              </NavLink>
            </nav>
          </div>
        )}

        {/* Demo Role Switcher box */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-blue-600" /> Role Preview
            </span>
            <span
              className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                isAdmin ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
              }`}
            >
              {isAdmin ? 'HR Admin' : 'Employee'}
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mb-2.5">
            Toggle between roles to verify employee chat vs. HR admin document indexing.
          </p>
          <button
            type="button"
            onClick={() => switchDemoRole(isAdmin ? 'EMPLOYEE' : 'HR_ADMIN')}
            className="w-full flex items-center justify-center gap-1.5 py-1.5 px-2.5 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 transition-colors shadow-xs cursor-pointer"
          >
            <RefreshCw className="w-3 h-3 text-slate-500" />
            Switch to {isAdmin ? 'Employee Role' : 'HR Admin Role'}
          </button>
        </div>
      </div>

      {/* User Footer */}
      <div className="p-3.5 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center justify-between gap-2 p-2 rounded-lg bg-white border border-slate-200/80">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-semibold text-xs flex items-center justify-center shrink-0 shadow-xs">
              {user?.avatar || 'U'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-slate-900 truncate leading-tight">
                {user?.name || 'Authorized User'}
              </p>
              <p className="text-[11px] text-slate-500 truncate leading-tight">
                {user?.region || 'Global'} · {user?.role === 'HR_ADMIN' ? 'HR Admin' : 'Employee'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            title="Sign out"
            aria-label="Sign out"
            className="text-slate-400 hover:text-rose-600 p-1.5 rounded-md hover:bg-rose-50 transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden md:flex w-64 flex-col fixed inset-y-0 left-0 z-30">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop & Sidebar */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
            onClick={closeMobile}
          />
          <div className="relative w-72 max-w-[85vw] h-full shadow-2xl z-10">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
