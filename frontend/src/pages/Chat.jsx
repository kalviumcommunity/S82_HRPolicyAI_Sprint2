// src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  PlusCircle,
  Clock,
  ShieldCheck,
  AlertCircle,
  HelpCircle,
  RefreshCw,
  Search,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { ChatMessage } from '../components/chat/ChatMessage';
import { ChatInput } from '../components/chat/ChatInput';
import { SourceModal } from '../components/chat/SourceModal';
import { Loading } from '../components/common/Loading';
import { Button } from '../components/common/Button';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export function Chat() {
  const [searchParams, setSearchParams] = useSearchParams();
  const convIdFromUrl = searchParams.get('id');

  const { user } = useAuth();

  const [conversationId, setConversationId] = useState(convIdFromUrl || null);
  const [conversationTitle, setConversationTitle] = useState('New HR Policy Consultation');
  const [messages, setMessages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingConv, setLoadingConv] = useState(false);
  const [queryStatus, setQueryStatus] = useState(''); // e.g. "Searching HR policies...", "Synthesizing answer..."
  const [error, setError] = useState(null);

  // Active source for the SourceModal
  const [activeSource, setActiveSource] = useState(null);

  const messagesEndRef = useRef(null);

  // Auto-scroll down when messages change or submitting
  const scrollToBottom = (behavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom('smooth');
  }, [messages, isSubmitting, queryStatus]);

  // Load existing conversation if id in URL changes
  useEffect(() => {
    async function loadConversation() {
      if (!convIdFromUrl) {
        // Reset to clean state or initial demo conversation
        setConversationId(null);
        setConversationTitle('New HR Policy Consultation');
        setMessages([]);
        return;
      }

      try {
        setLoadingConv(true);
        setError(null);
        const data = await api.chat.getConversation(convIdFromUrl);
        setConversationId(data.id);
        setConversationTitle(data.title);
        setMessages(data.messages || []);
      } catch (err) {
        console.error('Failed to load conversation:', err);
        setError('Unable to load requested conversation history.');
      } finally {
        setLoadingConv(false);
      }
    }

    loadConversation();
  }, [convIdFromUrl]);

  const handleStartNewChat = () => {
    setSearchParams({});
    setConversationId(null);
    setConversationTitle('New HR Policy Consultation');
    setMessages([]);
    setError(null);
  };

  const handleSendMessage = async (questionText) => {
    setError(null);
    const userTimestamp = new Date().toISOString();

    const tempUserMessage = {
      id: `tmp_${Date.now()}`,
      conversation_id: conversationId,
      sender: 'user',
      text: questionText,
      timestamp: userTimestamp,
    };

    // Optimistically show user question immediately
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsSubmitting(true);
    setQueryStatus('Searching HR policy knowledge base...');

    // Small status transition for realistic RAG pipeline feedback
    const timer = setTimeout(() => {
      setQueryStatus('Retrieving policy excerpts & formulating response...');
    }, 400);

    try {
      const response = await api.chat.sendMessage({
        conversation_id: conversationId,
        question: questionText,
      });

      clearTimeout(timer);

      // Set or update active conversation id
      if (!conversationId) {
        setConversationId(response.conversation_id);
        setSearchParams({ id: response.conversation_id });
        setConversationTitle(questionText.slice(0, 35) + '...');
      }

      const aiMessage = {
        id: response.message_id || `msg_ai_${Date.now()}`,
        conversation_id: response.conversation_id,
        sender: 'assistant',
        text: response.answer,
        timestamp: new Date().toISOString(),
        sources: response.sources || [],
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      clearTimeout(timer);
      console.error('Chat error:', err);
      setError(err.message || 'Unable to retrieve policy information. Please try again.');
    } finally {
      setIsSubmitting(false);
      setQueryStatus('');
    }
  };

  return (
    <PageContainer
      title={conversationTitle}
      subtitle={`Policy Assistant · Employee: ${user?.name || 'Authorized'} (${user?.region || 'India'})`}
      fullWidth
    >
      <div className="flex flex-col h-[calc(100vh-4rem)] bg-slate-50">
        {/* Chat Actions Top Toolbar */}
        <div className="bg-white px-4 sm:px-6 py-2.5 border-b border-slate-200 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
              <span>Official Knowledge Base</span>
            </span>
            <span className="hidden sm:inline text-xs text-slate-400">|</span>
            <span className="hidden sm:inline text-xs text-slate-500">
              All responses include verifiable source citations
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={PlusCircle}
              onClick={handleStartNewChat}
              className="text-xs"
            >
              New Query
            </Button>
          </div>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
          <div className="max-w-4xl mx-auto">
            {loadingConv ? (
              <Loading message="Loading conversation history..." className="my-16" />
            ) : error && messages.length === 0 ? (
              <div className="my-12 p-6 bg-rose-50 border border-rose-200 rounded-xl text-center max-w-md mx-auto">
                <AlertCircle className="w-8 h-8 text-rose-600 mx-auto mb-2" />
                <h4 className="font-semibold text-rose-900 text-sm">Failed to load chat</h4>
                <p className="text-xs text-rose-700 mt-1 mb-4">{error}</p>
                <Button variant="outline" size="sm" onClick={handleStartNewChat}>
                  Start fresh conversation
                </Button>
              </div>
            ) : messages.length === 0 ? (
              /* Empty state / Welcome screen */
              <div className="py-8 sm:py-14 text-center max-w-2xl mx-auto">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center mx-auto shadow-md shadow-blue-500/20 mb-4">
                  <Sparkles className="w-7 h-7" />
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 mb-2">
                  Welcome to HRPolicyAI Assistant
                </h3>
                <p className="text-sm text-slate-500 max-w-lg mx-auto mb-8 leading-relaxed">
                  Ask any question regarding official company policies, leave entitlements, health
                  benefits, parental leaves, or hybrid work schedules. Every answer is grounded directly
                  in company HR documentation with clickable citations.
                </p>

                {/* Feature highlight cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl shadow-2xs">
                    <span className="font-semibold text-xs text-slate-900 block mb-1">
                      Exact Policy Answers
                    </span>
                    <p className="text-[11px] text-slate-500 leading-normal">
                      Grounded in vetted PDF & DOCX manuals indexed in our internal ChromaDB vector database.
                    </p>
                  </div>
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl shadow-2xs">
                    <span className="font-semibold text-xs text-slate-900 block mb-1">
                      Verifiable Citations
                    </span>
                    <p className="text-[11px] text-slate-500 leading-normal">
                      Every statement links to the exact section, page number, and original policy excerpt.
                    </p>
                  </div>
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl shadow-2xs">
                    <span className="font-semibold text-xs text-slate-900 block mb-1">
                      Region Aware
                    </span>
                    <p className="text-[11px] text-slate-500 leading-normal">
                      Tailored specifically to your designated office location ({user?.region || 'India'}).
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              /* Message list */
              <div>
                {messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    message={msg}
                    onSelectSource={(source) => setActiveSource(source)}
                  />
                ))}

                {/* Live RAG Thinking / Searching indicator */}
                {isSubmitting && (
                  <div className="flex justify-start mb-6">
                    <div className="flex items-start gap-3 max-w-2xl">
                      <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                        <Sparkles className="w-4 h-4 animate-spin" />
                      </div>
                      <div className="bg-white border border-blue-200 rounded-2xl rounded-tl-xs p-4 shadow-xs">
                        <div className="flex items-center gap-2 text-xs font-medium text-blue-700 mb-1">
                          <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
                          <span>{queryStatus || 'Searching policy documents...'}</span>
                        </div>
                        <p className="text-xs text-slate-400">
                          Retrieving chunks from vector store & preparing cited response...
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Inline submission error */}
                {error && (
                  <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                      <span>{error}</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Composer Area */}
        <ChatInput
          onSendMessage={handleSendMessage}
          isSubmitting={isSubmitting}
          showSuggestions={messages.length === 0}
        />
      </div>

      {/* Citation Modal */}
      <SourceModal
        isOpen={!!activeSource}
        onClose={() => setActiveSource(null)}
        source={activeSource}
      />
    </PageContainer>
  );
}
