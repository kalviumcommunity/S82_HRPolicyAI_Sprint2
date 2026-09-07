// src/components/chat/SourceModal.jsx
import React, { useState } from 'react';
import { FileText, Copy, Check, ExternalLink, MapPin, Tag } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';

export function SourceModal({ isOpen, onClose, source }) {
  const [copied, setCopied] = useState(false);

  if (!source) return null;

  const handleCopyExcerpt = () => {
    if (source.excerpt) {
      navigator.clipboard.writeText(source.excerpt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Policy Citation & Excerpt"
      subtitle={`Verified excerpt from ${source.document || 'HR Policy Document'}`}
      maxWidth="max-w-2xl"
      footer={
        <div className="flex items-center justify-between w-full">
          <button
            type="button"
            onClick={handleCopyExcerpt}
            className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium px-2.5 py-1.5 rounded-md hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700 font-semibold">Excerpt copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy excerpt</span>
              </>
            )}
          </button>
          <Button variant="primary" size="sm" onClick={onClose}>
            Close Citation
          </Button>
        </div>
      }
    >
      <div className="space-y-4">
        {/* Document Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
          <div>
            <span className="text-slate-400 block mb-0.5">Document</span>
            <span className="font-semibold text-slate-800 break-words">{source.document}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Section</span>
            <span className="font-medium text-slate-700">{source.section || 'General'}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Page / Location</span>
            <span className="font-medium text-slate-700">
              {source.page ? `Page ${source.page}` : 'Reference section'}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Region & Version</span>
            <span className="font-medium text-slate-700">
              {source.region || 'Global'} · v{source.version || '2026'}
            </span>
          </div>
        </div>

        {/* Excerpt Body */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Relevant Policy Excerpt
          </label>
          <div className="p-4 bg-amber-50/60 border border-amber-200/80 rounded-lg text-slate-800 text-sm leading-relaxed font-serif relative">
            <span className="text-2xl font-serif text-amber-300 absolute -top-1.5 left-2 select-none">
              “
            </span>
            <p className="pl-4 italic">
              {source.excerpt || 'No specific excerpt text available for this citation.'}
            </p>
          </div>
        </div>

        {/* RAG Verification Note */}
        <div className="p-3 bg-blue-50/60 border border-blue-100 rounded-lg text-xs text-blue-900 flex items-start gap-2">
          <FileText className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
          <p>
            This chunk was retrieved from ChromaDB vector index and matched against current internal
            HR policy files using semantic similarity.
          </p>
        </div>
      </div>
    </Modal>
  );
}
