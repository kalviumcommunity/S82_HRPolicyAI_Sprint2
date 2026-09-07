// src/components/chat/ChatInput.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, CornerDownLeft } from 'lucide-react';
import { Button } from '../common/Button';

export function ChatInput({ onSendMessage, isSubmitting, placeholder, showSuggestions = false }) {
  const [question, setQuestion] = useState('');
  const textareaRef = useRef(null);

  const suggestions = [
    'How many annual leave days can I take?',
    'What is the parental leave duration for new parents?',
    'Does our health insurance cover dependent parents in India?',
    'What are the core hours for hybrid work?',
  ];

  // Auto-resize textarea as text grows
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [question]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || isSubmitting) return;

    onSendMessage(trimmed);
    setQuestion('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestionClick = (promptText) => {
    if (isSubmitting) return;
    onSendMessage(promptText);
  };

  return (
    <div className="w-full bg-white border-t border-slate-200 p-3 sm:p-4 shadow-xs">
      <div className="max-w-4xl mx-auto">
        {/* Quick prompt suggestions chips */}
        {showSuggestions && (
          <div className="mb-3">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium mb-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Suggested policy questions:</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {suggestions.map((promptText, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSuggestionClick(promptText)}
                  disabled={isSubmitting}
                  className="text-xs bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 hover:border-blue-200 px-2.5 py-1 rounded-full transition-colors cursor-pointer text-left truncate max-w-xs"
                >
                  {promptText}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Form Composer */}
        <form onSubmit={handleSubmit} className="relative flex items-end gap-2 bg-slate-50 border border-slate-300 rounded-xl p-2 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 focus-within:bg-white transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSubmitting}
            placeholder={placeholder || 'Ask any HR policy question (e.g., leave entitlement, insurance, benefits)...'}
            className="flex-1 bg-transparent border-0 resize-none text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-0 max-h-36 py-1.5 px-2 leading-relaxed"
          />

          <div className="flex items-center gap-1.5 shrink-0">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={!question.trim() || isSubmitting}
              isLoading={isSubmitting}
              icon={isSubmitting ? null : Send}
              className="rounded-lg h-9 px-3"
            >
              <span className="hidden sm:inline">Send</span>
            </Button>
          </div>
        </form>

        <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 px-1">
          <span className="flex items-center gap-1">
            <CornerDownLeft className="w-3 h-3" /> Press <strong className="text-slate-500">Enter</strong> to send, <strong className="text-slate-500">Shift + Enter</strong> for newline
          </span>
          <span className="hidden sm:inline">Verified against corporate HR documents</span>
        </div>
      </div>
    </div>
  );
}
