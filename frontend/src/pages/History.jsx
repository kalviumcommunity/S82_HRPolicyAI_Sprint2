// src/pages/History.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Search, MessageSquare, Plus, RefreshCw } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { ConversationCard } from '../components/history/ConversationCard';
import { Loading } from '../components/common/Loading';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { Button } from '../components/common/Button';
import { api } from '../services/api';

export function History() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.chat.getConversations();
      setConversations(data || []);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError(err.message || 'Unable to load conversation history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSelectConversation = (id) => {
    navigate(`/chat?id=${id}`);
  };

  const handleDeleteConversation = async (id) => {
    try {
      await api.chat.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      alert('Unable to delete conversation.');
    }
  };

  const filteredConversations = conversations.filter((c) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return (
      c.title?.toLowerCase().includes(term) ||
      c.preview?.toLowerCase().includes(term) ||
      c.region?.toLowerCase().includes(term)
    );
  });

  return (
    <PageContainer
      title="Conversation History"
      subtitle="View and resume previous policy consultations and legal inquiries"
    >
      <div className="space-y-6">
        {/* Header toolbar with Search and New Chat button */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search previous policy queries or keywords..."
              className="w-full text-xs sm:text-sm pl-9 pr-4 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={RefreshCw}
              onClick={loadHistory}
              title="Refresh conversation list"
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Plus}
              onClick={() => navigate('/chat')}
            >
              New HR Query
            </Button>
          </div>
        </div>

        {/* Content list */}
        {loading ? (
          <Loading message="Loading conversation history..." className="py-16" />
        ) : error ? (
          <ErrorState
            title="Failed to load history"
            message={error}
            onRetry={loadHistory}
          />
        ) : filteredConversations.length === 0 ? (
          <EmptyState
            title={searchTerm ? 'No matching conversations' : 'No conversations yet'}
            description={
              searchTerm
                ? `No past conversations matched "${searchTerm}". Try a different keyword.`
                : 'Start a consultation with HRPolicyAI to have your queries answered and saved.'
            }
            icon={MessageSquare}
            actionLabel="Start New Conversation"
            onAction={() => navigate('/chat')}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredConversations.map((conversation) => (
              <ConversationCard
                key={conversation.id}
                conversation={conversation}
                onSelect={handleSelectConversation}
                onDelete={handleDeleteConversation}
              />
            ))}
          </div>
        )}
      </div>
    </PageContainer>
  );
}
