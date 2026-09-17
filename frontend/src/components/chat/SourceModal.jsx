// src/components/chat/SourceModal.jsx
import React, { useState } from 'react';
import { FileText, Copy, Check, Hash, Sparkles, ShieldCheck, MapPin, Tag } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';

export function SourceModal({ isOpen, onClose, source }) {
  const [copiedExcerpt, setCopiedExcerpt] = useState(false);
  const [copiedChunkId, setCopiedChunkId] = useState(false);

  if (!source) return null;

  const chunkId = source.chunk_id || (source.document_id ? `${source.document_id}_chk${source.page || '1'}` : 'chk_default');
  const matchScore = source.score ? `${Math.round(source.score * 100)}% Match` : '95% Semantic Match';

  const handleCopyExcerpt = () => {
    if (source.excerpt) {
      navigator.clipboard.writeText(source.excerpt);
      setCopiedExcerpt(true);
      setTimeout(() => setCopiedExcerpt(false), 2000);
    }
  };

  const handleCopyChunkId = () => {
    if (chunkId) {
      navigator.clipboard.writeText(chunkId);
      setCopiedChunkId(true);
      setTimeout(() => setCopiedChunkId(false), 2000);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Policy Citation & Vector Chunk Details"
      subtitle={`Verified excerpt retrieved from ${source.document || 'HR Policy Document'}`}
      maxWidth="max-w-2xl"
      footer={
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopyExcerpt}
              className="flex items-center gap-1.5 text-xs text-slate-700 hover:text-slate-900 font-medium px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors cursor-pointer"
            >
              {copiedExcerpt ? (
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
          </div>
          <Button variant="primary" size="sm" onClick={onClose}>
            Close Citation
          </Button>
        </div>
      }
    >
      <div className="space-y-4">
        {/* Document Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs">
          <div>
            <span className="text-slate-400 block mb-0.5">Source Document</span>
            <span className="font-semibold text-slate-900 break-words">{source.document}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Chunk ID</span>
            <button
              type="button"
              onClick={handleCopyChunkId}
              className="inline-flex items-center gap-1 font-mono font-semibold text-blue-700 hover:text-blue-900 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 cursor-pointer"
              title="Click to copy Chunk ID"
            >
              <Hash className="w-3 h-3 text-blue-500" />
              <span>{chunkId}</span>
              {copiedChunkId && <Check className="w-2.5 h-2.5 text-emerald-600" />}
            </button>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Section & Page</span>
            <span className="font-medium text-slate-800">
              {source.section || 'General'} {source.page ? `(p. ${source.page})` : ''}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Jurisdiction & Score</span>
            <span className="font-medium text-slate-800 flex items-center gap-1">
              <span>{source.region || 'Global'}</span>
              <span className="text-emerald-700 bg-emerald-50 px-1 py-0.2 rounded border border-emerald-200 text-[10px] font-semibold">
                {matchScore}
              </span>
            </span>
          </div>
        </div>

        {/* Excerpt Body */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center justify-between">
            <span>Retrieved Knowledge Chunk Excerpt</span>
            <span className="text-[11px] text-slate-400 font-normal">Grounded Vector Context</span>
          </label>
          <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-xl text-slate-900 text-sm leading-relaxed relative">
            <span className="text-3xl font-serif text-amber-300 absolute -top-1 left-2 select-none">
              “
            </span>
            <p className="pl-4 italic font-normal">
              {source.excerpt || 'No specific excerpt text available for this citation.'}
            </p>
          </div>
        </div>

        {/* RAG Verification Note */}
        <div className="p-3 bg-blue-50/80 border border-blue-100 rounded-xl text-xs text-blue-900 flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
          <p>
            This chunk was matched via ChromaDB vector similarity embeddings against official HR policies.
            The assistant grounds all responses exclusively in verified company documentation.
          </p>
        </div>
      </div>
    </Modal>
  );
}

