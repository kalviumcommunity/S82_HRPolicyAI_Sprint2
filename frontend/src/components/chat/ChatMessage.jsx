// src/components/chat/ChatMessage.jsx
import React, { useState } from 'react';
import { Sparkles, User, Copy, Check, ThumbsUp, ThumbsDown, ShieldCheck, BookOpen, Layers, Zap } from 'lucide-react';
import { SourceCard } from './SourceCard';

export function ChatMessage({ message, onSelectSource }) {
  const isUser = message.sender === 'user';
  const isStreaming = message.isStreaming || false;
  const isCacheHit = message.cache_hit || false;
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null); // 'like' | 'dislike'

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Find source corresponding to a citation number like [1] or [2]
  const findSourceForCitation = (citationNum) => {
    if (!message.sources || !message.sources.length) return null;
    const num = parseInt(citationNum, 10);
    // Try matching citation_index first
    const byIndex = message.sources.find((s) => s.citation_index === num);
    if (byIndex) return byIndex;
    // Otherwise fallback to 0-based array index
    return message.sources[num - 1] || message.sources[0];
  };

  const handleCitationClick = (citationNum) => {
    const src = findSourceForCitation(citationNum);
    if (src && onSelectSource) {
      onSelectSource(src);
    }
  };

  // Parse text line and replace [1], [2] with interactive citation buttons
  const parseInlineCitations = (lineText, lineKey) => {
    const citationRegex = /\[(\d+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = citationRegex.exec(lineText)) !== null) {
      const matchIndex = match.index;
      const citationNum = match[1];

      // Push preceding text if any
      if (matchIndex > lastIndex) {
        parts.push(lineText.substring(lastIndex, matchIndex));
      }

      // Push interactive citation pill
      parts.push(
        <button
          key={`cite-${lineKey}-${matchIndex}`}
          type="button"
          onClick={() => handleCitationClick(citationNum)}
          title={`Click to view Source [${citationNum}] citation excerpt`}
          className="inline-flex items-center justify-center font-bold text-[10px] bg-blue-100 hover:bg-blue-200 text-blue-700 hover:text-blue-900 px-1.5 py-0.2 mx-0.5 rounded border border-blue-300 align-baseline cursor-pointer transition-all shadow-2xs hover:scale-105"
        >
          [{citationNum}]
        </button>
      );

      lastIndex = citationRegex.lastIndex;
    }

    if (lastIndex < lineText.length) {
      parts.push(lineText.substring(lastIndex));
    }

    return parts.length > 0 ? parts : lineText;
  };

  // Format line breaks and simple markdown bullets nicely
  const renderFormattedText = (text) => {
    if (!text) return null;
    const lines = text.split('\n');

    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
        const bulletText = trimmed.replace(/^[•-]\s*/, '');
        return (
          <li key={idx} className="ml-4 list-disc text-slate-800 my-0.5">
            {parseInlineCitations(bulletText, idx)}
          </li>
        );
      }
      if (!trimmed) {
        return <div key={idx} className="h-2" />;
      }
      return (
        <p key={idx} className="mb-1.5 last:mb-0 leading-relaxed">
          {parseInlineCitations(line, idx)}
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
          <Sparkles className={`w-4 h-4 ${isStreaming ? 'animate-spin' : ''}`} />
        </div>

        <div className="flex-1 bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 sm:p-5 shadow-xs transition-all">
          {/* Header with Grounded Badge & Cache Hit indicator */}
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-100 flex-wrap gap-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800 flex-wrap">
              <span>HRPolicyAI</span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <ShieldCheck className="w-3 h-3" /> Grounded in Policy
              </span>
              {isCacheHit && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200 shadow-2xs">
                  <Zap className="w-2.5 h-2.5 text-amber-600 fill-amber-500" />
                  Cached (Instant · 0.00s)
                </span>
              )}
              {isStreaming && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200 animate-pulse">
                  Streaming answer...
                </span>
              )}
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

          {/* AI Response Text with Inline Citations and Streaming Cursor */}
          <div className="text-sm text-slate-800 font-normal">
            {renderFormattedText(message.text)}
            {isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-blue-600 animate-pulse align-middle" />
            )}
          </div>

          {/* Policy Citations / Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-3.5 border-t border-slate-100">
              <div className="flex items-center justify-between mb-2.5">
                <div className="flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-blue-600" />
                  <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Cited Policy Sources ({message.sources.length})
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">Click marker [1] or card to view excerpts</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {message.sources.map((src, index) => (
                  <SourceCard
                    key={`${src.document_id || index}-${index}`}
                    source={src}
                    citationIndex={src.citation_index || index + 1}
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
                : 'Just now'}
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
