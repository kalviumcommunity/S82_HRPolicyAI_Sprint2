// src/components/chat/SourceCard.jsx
import React from 'react';
import { BookOpen, ChevronRight, Hash, Sparkles } from 'lucide-react';

export function SourceCard({ source, onSelect }) {
  if (!source) return null;

  const chunkId = source.chunk_id || (source.document_id ? `${source.document_id}_chk${source.page || '1'}` : null);
  const matchScore = source.score ? `${Math.round(source.score * 100)}% Match` : 'High Relevance';

  return (
    <div className="group flex flex-col justify-between p-3.5 bg-white hover:bg-blue-50/50 border border-slate-200 hover:border-blue-300 rounded-xl transition-all duration-200 shadow-xs hover:shadow-sm">
      <div>
        {/* Top Header with Document Name & Score */}
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-1.5 min-w-0">
            <BookOpen className="w-4 h-4 text-blue-600 shrink-0" />
            <h5 className="text-xs font-semibold text-slate-900 group-hover:text-blue-700 truncate">
              {source.document || 'Policy Reference'}
            </h5>
          </div>
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
            <Sparkles className="w-2.5 h-2.5" />
            {matchScore}
          </span>
        </div>

        {/* Section & Page Metadata */}
        <p className="text-[11px] text-slate-600 font-medium truncate mb-1">
          {source.section || 'General Section'} {source.page ? `· Page ${source.page}` : ''}
        </p>

        {/* Chunk ID and Region Tags */}
        <div className="flex flex-wrap items-center gap-1.5 mt-2">
          {chunkId && (
            <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-mono border border-slate-200">
              <Hash className="w-2.5 h-2.5 text-slate-400" />
              {chunkId}
            </span>
          )}
          <span className="px-1.5 py-0.5 rounded bg-slate-50 text-slate-500 text-[10px] border border-slate-200">
            {source.region || 'Global'}
          </span>
          <span className="px-1.5 py-0.5 rounded bg-slate-50 text-slate-500 text-[10px] border border-slate-200">
            v{source.version || '2026'}
          </span>
        </div>
      </div>

      {/* Action Footer */}
      <button
        type="button"
        onClick={() => onSelect(source)}
        className="mt-3 flex items-center justify-between w-full text-[11px] font-semibold text-blue-600 group-hover:text-blue-700 transition-colors pt-2.5 border-t border-slate-100 cursor-pointer"
      >
        <span>View Source Excerpt & Context</span>
        <ChevronRight className="w-3.5 h-3.5 transform group-hover:translate-x-0.5 transition-transform" />
      </button>
    </div>
  );
}

