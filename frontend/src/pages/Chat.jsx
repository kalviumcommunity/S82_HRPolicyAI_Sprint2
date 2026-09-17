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
  const [isStreaming, setIsStreaming] = useState(false);
  const [loadingConv, setLoadingConv] = useState(false);
  const [queryStatus, setQueryStatus] = useState('');
  const [error, setError] = useState(null);
  const [lastQuestion, setLastQuestion] = useState('');

  // Active source for the SourceModal
  const [activeSource, setActiveSource] = useState(null);

  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Auto-scroll down when messages change or submitting
  const scrollToBottom = (behavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom('smooth');
  }, [messages, isSubmitting, isStreaming, queryStatus]);

  // Load existing conversation if id in URL changes
  useEffect(() => {
    if (convIdFromUrl && convIdFromUrl === conversationId) {
      return;
    }

    async function loadConversation() {
      if (!convIdFromUrl) {
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
        setError('Unable to load requested conversation history. Please check your network or try again.');
      } finally {
        setLoadingConv(false);
      }
    }

    loadConversation();
  }, [convIdFromUrl, conversationId]);

  const handleStartNewChat = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setSearchParams({});
    setConversationId(null);
    setConversationTitle('New HR Policy Consultation');
    setMessages([]);
    setError(null);
    setLastQuestion('');
    setIsSubmitting(false);
    setIsStreaming(false);
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsSubmitting(false);
    setIsStreaming(false);
    setQueryStatus('');
    // Finalize any streaming messages
    setMessages((prev) =>
      prev.map((msg) => (msg.isStreaming ? { ...msg, isStreaming: false } : msg))
    );
  };

  const handleSendMessage = async (questionText) => {
    if (!questionText.trim() || isSubmitting) return;

    setError(null);
    setLastQuestion(questionText);
    const userTimestamp = new Date().toISOString();

    const tempUserMessage = {
      id: `tmp_u_${Date.now()}`,
      conversation_id: conversationId,
      sender: 'user',
      text: questionText,
      timestamp: userTimestamp,
    };

    const tempAiMessageId = `tmp_ai_${Date.now()}`;
    const tempAiMessage = {
      id: tempAiMessageId,
      conversation_id: conversationId,
      sender: 'assistant',
      text: '',
      timestamp: new Date().toISOString(),
      sources: [],
      isStreaming: true,
    };

    // Optimistically show user question and streaming AI container
    setMessages((prev) => [...prev, tempUserMessage, tempAiMessage]);
    setIsSubmitting(true);
    setIsStreaming(true);
    setQueryStatus('Searching ChromaDB vector index & extracting policy chunks...');

    // Setup abort controller for stream interruption support
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await api.chat.sendMessageStream({
        conversation_id: conversationId,
        question: questionText,
        signal: controller.signal,
        onSources: (incomingSources) => {
          setQueryStatus('Streaming grounded answer with citations...');
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempAiMessageId
                ? { ...msg, sources: incomingSources }
                : msg
            )
          );
        },
        onChunk: (_token, accumulatedText) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempAiMessageId
                ? { ...msg, text: accumulatedText }
                : msg
            )
          );
        },
        onDone: (finalResult) => {
          if (!conversationId && finalResult?.conversation_id) {
            setConversationId(finalResult.conversation_id);
            setSearchParams({ id: finalResult.conversation_id });
            setConversationTitle(questionText.slice(0, 35) + '...');
          }

          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempAiMessageId
                ? {
                    ...msg,
                    id: finalResult?.message_id || msg.id,
                    text: finalResult?.answer || msg.text,
                    sources: finalResult?.sources || msg.sources,
                    isStreaming: false,
                  }
                : msg
            )
          );
        },
        onError: (err) => {
          throw err;
        },
      });
    } catch (err) {
      if (controller.signal.aborted) {
        // Handled cleanly by stop button
        return;
      }
      console.error('Streaming error:', err);
      setError(
        err.message ||
          'Connection interrupted while streaming response. Please check your network and try again.'
      );

      // Finalize or remove empty streaming message on error
      setMessages((prev) => {
        const streamMsg = prev.find((m) => m.id === tempAiMessageId);
        if (streamMsg && !streamMsg.text) {
          return prev.filter((m) => m.id !== tempAiMessageId);
        }
        return prev.map((m) =>
          m.id === tempAiMessageId ? { ...m, isStreaming: false } : m
        );
      });
    } finally {
      setIsSubmitting(false);
      setIsStreaming(false);
      setQueryStatus('');
      abortControllerRef.current = null;
    }
  };

  const handleRetryLast = () => {
    if (lastQuestion) {
      // Remove failed transient messages
      setMessages((prev) => prev.filter((m) => !m.id.startsWith('tmp_')));
      handleSendMessage(lastQuestion);
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

                {/* Inline submission error with Retry & Dismiss */}
                {error && (
                  <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
                    <div className="flex items-start sm:items-center gap-2.5">
                      <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5 sm:mt-0" />
                      <div>
                        <span className="font-semibold block sm:inline mr-1">Query Failed:</span>
                        <span>{error}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
                      {lastQuestion && (
                        <button
                          type="button"
                          onClick={handleRetryLast}
                          className="flex items-center gap-1 px-2.5 py-1 bg-white border border-rose-300 hover:bg-rose-100 text-rose-700 font-semibold rounded-lg text-xs transition-colors cursor-pointer"
                        >
                          <RefreshCw className="w-3 h-3" />
                          <span>Retry</span>
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => setError(null)}
                        className="px-2 py-1 text-slate-500 hover:text-slate-800 hover:bg-rose-100 rounded-lg text-xs transition-colors cursor-pointer"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Composer Area with progressive streaming and stop controls */}
        <ChatInput
          onSendMessage={handleSendMessage}
          isSubmitting={isSubmitting}
          isStreaming={isStreaming}
          onStopGeneration={handleStopGeneration}
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
