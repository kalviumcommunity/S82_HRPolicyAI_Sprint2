// src/components/layout/PageContainer.jsx
import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function PageContainer({ title, subtitle, children, fullWidth = false }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar Navigation */}
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      {/* Main App Layout Area */}
      <div className="flex-1 flex flex-col md:pl-64 min-w-0">
        <Topbar
          title={title}
          subtitle={subtitle}
          onMenuClick={() => setMobileOpen(true)}
        />

        <main className={`flex-1 ${fullWidth ? 'p-0' : 'p-4 sm:p-6 md:p-8'} overflow-y-auto`}>
          <div className={`${fullWidth ? 'h-full' : 'max-w-7xl mx-auto'}`}>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
