// src/components/chat/SourceCard.jsx
import React from 'react';
import { BookOpen, ChevronRight } from 'lucide-react';

export function SourceCard({ source, onSelect }) {
  if (!source) return null;

  return (
    <div className="group flex flex-col justify-between p-3 bg-white hover:bg-blue-50/40 border border-slate-200 hover:border-blue-300 rounded-lg transition-all duration-150 shadow-xs">
      <div>
        <div className="flex items-center gap-1.5 mb-1">
          <BookOpen className="w-3.5 h-3.5 text-blue-600 shrink-0" />
          <h5 className="text-xs font-semibold text-slate-900 group-hover:text-blue-700 truncate">
            {source.document || 'Policy Reference'}
          </h5>
        </div>
        <p className="text-[11px] text-slate-500 truncate">
          {source.section || 'General'} {source.page ? `· Page ${source.page}` : ''}
        </p>
        <p className="text-[10px] text-slate-400 mt-0.5">
          v{source.version || '2026'} · {source.region || 'Global'}
        </p>
      </div>

      <button
        type="button"
        onClick={() => onSelect(source)}
        className="mt-2.5 flex items-center justify-between w-full text-[11px] font-semibold text-blue-600 hover:text-blue-800 transition-colors pt-2 border-t border-slate-100 cursor-pointer"
      >
        <span>View Source Excerpt</span>
        <ChevronRight className="w-3.5 h-3.5 transform group-hover:translate-x-0.5 transition-transform" />
      </button>
    </div>
  );
}
