// src/components/documents/DocumentStatus.jsx
import React from 'react';
import { CheckCircle2, Loader2, AlertTriangle } from 'lucide-react';

export function DocumentStatus({ status = 'Indexed', errorReason }) {
  const normalized = (status || '').toLowerCase();

  if (normalized === 'indexed') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
        <span>Indexed</span>
      </span>
    );
  }

  if (normalized === 'processing') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
        <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-600 shrink-0" />
        <span>Extracting & Indexing</span>
      </span>
    );
  }

  return (
    <span
      title={errorReason || 'Document extraction or chunk indexing failed'}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200 cursor-help"
    >
      <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
      <span>Failed</span>
    </span>
  );
}
