// src/components/history/ConversationCard.jsx
import React from 'react';
import { MessageSquare, Calendar, Globe, Trash2, ArrowRight } from 'lucide-react';

export function ConversationCard({ conversation, onSelect, onDelete }) {
  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation history?')) {
      onDelete(conversation.id);
    }
  };

  return (
    <div
      onClick={() => onSelect(conversation.id)}
      className="group p-4 sm:p-5 bg-white hover:bg-slate-50/80 border border-slate-200 hover:border-blue-300 rounded-xl transition-all duration-150 shadow-xs cursor-pointer flex flex-col justify-between"
    >
      <div>
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <MessageSquare className="w-4 h-4" />
            </div>
            <h3 className="font-semibold text-sm sm:text-base text-slate-900 group-hover:text-blue-700 transition-colors line-clamp-1">
              {conversation.title || 'Untitled Conversation'}
            </h3>
          </div>
          {onDelete && (
            <button
              type="button"
              onClick={handleDelete}
              title="Delete conversation"
              className="text-slate-300 hover:text-rose-600 p-1 rounded transition-colors opacity-0 group-hover:opacity-100 cursor-pointer"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>

        <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-4">
          {conversation.preview || 'No preview message available.'}
        </p>
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400 pt-3 border-t border-slate-100">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            {conversation.date || 'Recent'}
          </span>
          <span className="flex items-center gap-1">
            <Globe className="w-3.5 h-3.5" />
            {conversation.region || 'Global'}
          </span>
        </div>

        <div className="flex items-center gap-1 text-blue-600 font-medium group-hover:translate-x-0.5 transition-transform">
          <span>Resume Chat</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
}
