// src/components/chat/ChatMessage.jsx
import React, { useState } from 'react';
import { Sparkles, User, Copy, Check, ThumbsUp, ThumbsDown, ShieldCheck } from 'lucide-react';
import { SourceCard } from './SourceCard';

export function ChatMessage({ message, onSelectSource }) {
  const isUser = message.sender === 'user';
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null); // 'like' | 'dislike'

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Format line breaks and simple markdown bullets nicely
  const renderFormattedText = (text) => {
    return text.split('\n').map((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
        return (
          <li key={idx} className="ml-4 list-disc text-slate-800 my-0.5">
            {trimmed.replace(/^[•-]\s*/, '')}
          </li>
        );
      }
      if (!trimmed) {
        return <div key={idx} className="h-2" />;
      }
      return (
        <p key={idx} className="mb-1.5 last:mb-0 leading-relaxed">
          {line}
        </p>
      );
    });
  };

  if (isUser) {
    return (
      <div className="flex justify-end mb-6">
        <div className="flex items-start gap-2.5 max-w-2xl flex-row-reverse">
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-semibold shrink-0 shadow-xs">
            <User className="w-4 h-4" />
          </div>
          <div className="bg-blue-600 text-white rounded-2xl rounded-tr-xs px-4 py-3 shadow-xs">
            <p className="text-sm font-normal leading-relaxed whitespace-pre-wrap">{message.text}</p>
            <div className="mt-1 text-right">
              <span className="text-[10px] text-blue-200">
                {message.timestamp
                  ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  : 'Just now'}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start gap-3 max-w-3xl w-full">
        <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs shadow-blue-500/20">
          <Sparkles className="w-4 h-4" />
        </div>

        <div className="flex-1 bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 sm:p-5 shadow-xs">
          {/* Header with Grounded Badge */}
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-100">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
              <span>HRPolicyAI</span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <ShieldCheck className="w-3 h-3" /> Grounded in Policy
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopy}
                title="Copy answer"
                className="text-slate-400 hover:text-slate-700 p-1 rounded transition-colors cursor-pointer"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* AI Response Text */}
          <div className="text-sm text-slate-800 font-normal">
            {renderFormattedText(message.text)}
          </div>

          {/* Policy Citations / Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-3.5 border-t border-slate-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Verified Policy Sources ({message.sources.length})
                </span>
                <span className="text-[11px] text-slate-400">Click to view relevant excerpts</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {message.sources.map((src, index) => (
                  <SourceCard
                    key={`${src.document_id || index}-${index}`}
                    source={src}
                    onSelect={onSelectSource}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Footer with Helpful Feedback */}
          <div className="mt-3.5 pt-2 flex items-center justify-between text-xs text-slate-400">
            <span>
              {message.timestamp
                ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : ''}
            </span>
            <div className="flex items-center gap-2">
              <span className="text-[11px]">Was this answer accurate?</span>
              <button
                type="button"
                onClick={() => setFeedback(feedback === 'like' ? null : 'like')}
                className={`p-1 rounded hover:bg-slate-100 transition-colors cursor-pointer ${
                  feedback === 'like' ? 'text-blue-600 font-bold' : 'text-slate-400'
                }`}
                title="Helpful"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setFeedback(feedback === 'dislike' ? null : 'dislike')}
                className={`p-1 rounded hover:bg-slate-100 transition-colors cursor-pointer ${
                  feedback === 'dislike' ? 'text-rose-600 font-bold' : 'text-slate-400'
                }`}
                title="Not helpful"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
