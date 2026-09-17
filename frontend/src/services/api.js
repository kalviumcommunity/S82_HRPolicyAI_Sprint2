// src/services/api.js
import {
  MOCK_USERS,
  MOCK_DOCUMENTS,
  MOCK_DASHBOARD_STATS,
  MOCK_CONVERSATIONS,
  MOCK_QA_DATABASE,
} from '../data/mockData';

// Configuration
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'https://s82-hrpolicyai-sprint2-1.onrender.com').replace(/\/+$/, '');
// If VITE_USE_MOCK_API is explicitly 'false', then use real network calls; otherwise default to mock mode.
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === 'true';

// Helper for real fetch calls with auth headers
async function fetchClient(endpoint, options = {}) {
  const token = localStorage.getItem('hr_token');
  const headers = {
    'Accept': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If request has body and not FormData, default to application/json
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      errorMessage = errorJson.detail || errorJson.message || errorMessage;
    } catch {
      // ignore
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

// In-memory mock stores for local session state
let mockLocalUsers = [...MOCK_USERS];
let mockLocalDocuments = [...MOCK_DOCUMENTS];
let mockLocalConversations = JSON.parse(JSON.stringify(MOCK_CONVERSATIONS));

// Artificial delay helper for realistic UX feedback
const delay = (ms = 400) => new Promise((resolve) => setTimeout(resolve, ms));

export const api = {
  auth: {
    async login({ email, password }) {
      if (!USE_MOCK) {
        return fetchClient('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
      }

      await delay(450);
      const user = mockLocalUsers.find(
        (u) => u.email.toLowerCase() === (email || '').toLowerCase()
      );

      if (!user) {
        throw new Error('Invalid email or password. Please check your credentials.');
      }

      if (user.password && password !== user.password) {
        throw new Error('Invalid password. Please check your credentials.');
      }

      if (password && password.length < 4) {
        throw new Error('Password must be at least 4 characters long.');
      }

      const safeUser = { ...user };
      delete safeUser.password;

      const token = `mock_jwt_token_${user.id}_${Date.now()}`;
      return {
        token,
        user: safeUser,
      };
    },

    async register({ name, email, password, region }) {
      if (!USE_MOCK) {
        return fetchClient('/auth/register', {
          method: 'POST',
          body: JSON.stringify({ name, email, password, region }),
        });
      }

      await delay(500);
      if (!name || !email || !password) {
        throw new Error('All required fields must be completed.');
      }

      const existing = mockLocalUsers.find(
        (u) => u.email.toLowerCase() === email.toLowerCase()
      );
      if (existing) {
        throw new Error('An account with this email address already exists.');
      }

      const newUser = {
        id: `usr_emp_${Date.now().toString().slice(-4)}`,
        name,
        email,
        role: 'EMPLOYEE',
        region: region || 'India',
        department: 'General',
        avatar: name.slice(0, 2).toUpperCase(),
        joinedDate: new Date().toISOString().split('T')[0],
      };

      mockLocalUsers.push(newUser);
      const token = `mock_jwt_token_${newUser.id}_${Date.now()}`;
      return {
        token,
        user: newUser,
      };
    },

    async me() {
      if (!USE_MOCK) {
        return fetchClient('/auth/me');
      }

      await delay(200);
      const storedUser = localStorage.getItem('hr_user');
      if (storedUser) {
        return JSON.parse(storedUser);
      }
      return null;
    },
  },

  chat: {
    async sendMessage({ conversation_id, question }) {
      if (!USE_MOCK) {
        return fetchClient('/chat', {
          method: 'POST',
          body: JSON.stringify({ conversation_id, question }),
        });
      }

      await delay(750); // Simulate RAG query + vector search + LLM generation

      const qLower = (question || '').toLowerCase();
      // Look for matched answer in mock QA database
      const matched = MOCK_QA_DATABASE.find((item) =>
        item.keywords.some((kw) => qLower.includes(kw))
      );

      const generatedAnswer = matched
        ? matched.answer
        : `Based on your query regarding "${question}", our company policy documents indicate that policies are administered according to regional jurisdiction and active employment status. Please refer to the specific HR guidelines for your region or contact your People Partner for exceptional cases.`;

      const generatedSources = matched
        ? matched.sources
        : [
            {
              document_id: 'doc_gl_handbook',
              document: 'Global Employee Handbook',
              section: 'Chapter 1: General Employment Principles',
              page: 5,
              region: 'Global',
              version: '2026.2',
              excerpt: 'Company policies apply to all employees worldwide unless superseded by regional addenda or statutory requirements.',
            },
          ];

      const activeConvId = conversation_id || `conv_${Date.now()}`;
      const userMsgId = `msg_u_${Date.now()}`;
      const aiMsgId = `msg_a_${Date.now() + 1}`;

      const userMessage = {
        id: userMsgId,
        conversation_id: activeConvId,
        sender: 'user',
        text: question,
        timestamp: new Date().toISOString(),
      };

      const aiMessage = {
        id: aiMsgId,
        conversation_id: activeConvId,
        sender: 'assistant',
        text: generatedAnswer,
        timestamp: new Date().toISOString(),
        sources: generatedSources,
      };

      // Update or create conversation in mock state
      let conv = mockLocalConversations.find((c) => c.id === activeConvId);
      if (!conv) {
        const title = question.length > 40 ? question.slice(0, 40) + '...' : question;
        conv = {
          id: activeConvId,
          title,
          region: 'India',
          date: 'Today',
          updatedAt: new Date().toISOString(),
          messageCount: 2,
          preview: generatedAnswer.slice(0, 80) + '...',
          messages: [userMessage, aiMessage],
        };
        mockLocalConversations.unshift(conv);
      } else {
        conv.messages.push(userMessage, aiMessage);
        conv.updatedAt = new Date().toISOString();
        conv.messageCount = conv.messages.length;
        conv.preview = generatedAnswer.slice(0, 80) + '...';
      }

      return {
        conversation_id: activeConvId,
        message_id: aiMsgId,
        answer: generatedAnswer,
        sources: generatedSources,
      };
    },

    async sendMessageStream({ conversation_id, question, onSources, onChunk, onDone, onError, signal }) {
      if (!USE_MOCK) {
        try {
          const token = localStorage.getItem('hr_token');
          const headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
          };
          if (token) headers['Authorization'] = `Bearer ${token}`;

          const response = await fetch(`${API_BASE_URL}/chat/stream`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ conversation_id, question }),
            signal,
          });

          if (!response.ok) {
            let errDetail = `Server returned HTTP ${response.status}`;
            try {
              const errJson = await response.json();
              errDetail = errJson.detail || errJson.message || errDetail;
            } catch {
              // fallback
            }
            throw new Error(errDetail);
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder('utf-8');
          let buffer = '';
          let accumulatedText = '';
          let finalData = null;

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || '';

            for (const block of lines) {
              if (!block.trim()) continue;
              let eventType = 'message';
              let dataStr = '';

              const eventLines = block.split('\n');
              for (const line of eventLines) {
                if (line.startsWith('event: ')) {
                  eventType = line.substring(7).trim();
                } else if (line.startsWith('data: ')) {
                  dataStr = line.substring(6).trim();
                }
              }

              if (dataStr) {
                try {
                  const parsed = JSON.parse(dataStr);
                  if (eventType === 'sources') {
                    if (onSources) onSources(parsed.sources || []);
                  } else if (eventType === 'token') {
                    accumulatedText += parsed.token || '';
                    if (onChunk) onChunk(parsed.token || '', accumulatedText);
                  } else if (eventType === 'done') {
                    finalData = parsed;
                    if (onDone) onDone(parsed);
                  } else if (eventType === 'error') {
                    throw new Error(parsed.error || 'Streaming error');
                  }
                } catch (e) {
                  if (eventType === 'error') throw e;
                }
              }
            }
          }

          return finalData;
        } catch (err) {
          if (signal?.aborted) {
            return null;
          }
          if (onError) onError(err);
          throw err;
        }
      }

      // Mock Streaming Implementation
      try {
        await delay(250);
        if (signal?.aborted) return null;

        const qLower = (question || '').toLowerCase();
        const matched = MOCK_QA_DATABASE.find((item) =>
          item.keywords.some((kw) => qLower.includes(kw))
        );

        const generatedAnswer = matched
          ? matched.answer
          : `Based on your query regarding "${question}", our company policy documents indicate that policies are administered according to regional jurisdiction and active employment status [1]. Please refer to the specific HR guidelines for your region or contact your People Partner for exceptional cases.`;

        const generatedSources = matched
          ? matched.sources
          : [
              {
                document_id: 'doc_gl_handbook',
                chunk_id: 'chk_gl_handbook_001',
                marker: '[1]',
                citation_index: 1,
                document: 'Global Employee Handbook',
                section: 'Chapter 1: General Employment Principles',
                page: 5,
                region: 'Global',
                version: '2026.2',
                score: 0.90,
                excerpt: 'Company policies apply to all employees worldwide unless superseded by regional addenda or statutory requirements.',
              },
            ];

        // Emit sources immediately at start of stream
        if (onSources) onSources(generatedSources);

        // Stream word by word
        const words = generatedAnswer.split(' ');
        let accumulated = '';
        const activeConvId = conversation_id || `conv_${Date.now()}`;
        const aiMsgId = `msg_a_${Date.now()}`;

        for (let i = 0; i < words.length; i++) {
          if (signal?.aborted) return null;
          const token = words[i] + (i < words.length - 1 ? ' ' : '');
          accumulated += token;
          if (onChunk) onChunk(token, accumulated);
          await delay(32);
        }

        const finalResult = {
          conversation_id: activeConvId,
          message_id: aiMsgId,
          answer: generatedAnswer,
          sources: generatedSources,
        };

        // Save to mock storage
        const userMsgId = `msg_u_${Date.now()}`;
        const userMessage = {
          id: userMsgId,
          conversation_id: activeConvId,
          sender: 'user',
          text: question,
          timestamp: new Date().toISOString(),
        };
        const aiMessage = {
          id: aiMsgId,
          conversation_id: activeConvId,
          sender: 'assistant',
          text: generatedAnswer,
          timestamp: new Date().toISOString(),
          sources: generatedSources,
        };

        let conv = mockLocalConversations.find((c) => c.id === activeConvId);
        if (!conv) {
          const title = question.length > 40 ? question.slice(0, 40) + '...' : question;
          conv = {
            id: activeConvId,
            title,
            region: 'India',
            date: 'Today',
            updatedAt: new Date().toISOString(),
            messageCount: 2,
            preview: generatedAnswer.slice(0, 80) + '...',
            messages: [userMessage, aiMessage],
          };
          mockLocalConversations.unshift(conv);
        } else {
          conv.messages.push(userMessage, aiMessage);
          conv.updatedAt = new Date().toISOString();
          conv.messageCount = conv.messages.length;
          conv.preview = generatedAnswer.slice(0, 80) + '...';
        }

        if (onDone) onDone(finalResult);
        return finalResult;
      } catch (err) {
        if (signal?.aborted) return null;
        if (onError) onError(err);
        throw err;
      }
    },

    async getConversations() {
      if (!USE_MOCK) {
        return fetchClient('/conversations');
      }

      await delay(300);
      return [...mockLocalConversations];
    },

    async getConversation(id) {
      if (!USE_MOCK) {
        return fetchClient(`/conversations/${id}`);
      }

      await delay(250);
      const conv = mockLocalConversations.find((c) => c.id === id);
      if (!conv) {
        throw new Error('Conversation not found.');
      }
      return { ...conv };
    },

    async deleteConversation(id) {
      if (!USE_MOCK) {
        return fetchClient(`/conversations/${id}`, { method: 'DELETE' });
      }

      await delay(200);
      mockLocalConversations = mockLocalConversations.filter((c) => c.id !== id);
      return { success: true, id };
    },
  },

  documents: {
    async getAll(filters = {}) {
      if (!USE_MOCK) {
        const params = new URLSearchParams();
        if (filters.search) params.append('search', filters.search);
        if (filters.region) params.append('region', filters.region);
        if (filters.category) params.append('category', filters.category);
        if (filters.status) params.append('status', filters.status);
        const query = params.toString() ? `?${params.toString()}` : '';
        return fetchClient(`/documents${query}`);
      }

      await delay(350);
      let list = [...mockLocalDocuments];

      if (filters.search) {
        const term = filters.search.toLowerCase();
        list = list.filter(
          (d) =>
            d.name.toLowerCase().includes(term) ||
            d.filename.toLowerCase().includes(term) ||
            d.category.toLowerCase().includes(term)
        );
      }

      if (filters.region && filters.region !== 'All') {
        list = list.filter((d) => d.region.toLowerCase() === filters.region.toLowerCase());
      }

      if (filters.category && filters.category !== 'All') {
        list = list.filter(
          (d) => d.category.toLowerCase() === filters.category.toLowerCase()
        );
      }

      if (filters.status && filters.status !== 'All') {
        list = list.filter((d) => d.status.toLowerCase() === filters.status.toLowerCase());
      }

      return list;
    },

    async getOne(id) {
      if (!USE_MOCK) {
        return fetchClient(`/documents/${id}`);
      }

      await delay(200);
      const doc = mockLocalDocuments.find((d) => d.id === id);
      if (!doc) {
        throw new Error('Document not found');
      }
      return { ...doc };
    },

    async upload(formData) {
      if (!USE_MOCK) {
        return fetchClient('/documents', {
          method: 'POST',
          body: formData,
        });
      }

      await delay(800); // Simulate upload + extraction & indexing

      // Extract form fields
      const file = formData.get('file');
      const name = formData.get('name') || (file ? file.name : 'Untitled Policy Document');
      const region = formData.get('region') || 'Global';
      const category = formData.get('category') || 'General';
      const version = formData.get('version') || '2026.0';
      const effectiveDate = formData.get('effectiveDate') || new Date().toISOString().split('T')[0];

      const newDoc = {
        id: `doc_${Date.now()}`,
        name,
        filename: file ? file.name : `${name.replace(/\s+/g, '_')}.pdf`,
        region,
        category,
        version,
        effectiveDate,
        status: 'Indexed',
        chunkCount: Math.floor(Math.random() * 200) + 40,
        fileSize: file ? `${(file.size / (1024 * 1024)).toFixed(1)} MB` : '1.4 MB',
        updatedAt: new Date().toISOString(),
        author: 'HR Admin',
      };

      mockLocalDocuments.unshift(newDoc);
      return newDoc;
    },

    async delete(id) {
      if (!USE_MOCK) {
        return fetchClient(`/documents/${id}`, {
          method: 'DELETE',
        });
      }

      await delay(300);
      mockLocalDocuments = mockLocalDocuments.filter((d) => d.id !== id);
      return { success: true, id };
    },

    async reindex(id) {
      if (!USE_MOCK) {
        return fetchClient(`/documents/${id}/reindex`, {
          method: 'POST',
        });
      }

      await delay(600);
      const doc = mockLocalDocuments.find((d) => d.id === id);
      if (doc) {
        doc.status = 'Indexed';
        doc.chunkCount = Math.floor(Math.random() * 150) + 80;
        doc.updatedAt = new Date().toISOString();
        delete doc.errorReason;
      }
      return { ...doc };
    },
  },

  admin: {
    async getStats() {
      if (!USE_MOCK) {
        return fetchClient('/admin/stats');
      }

      await delay(300);
      const totalDocs = mockLocalDocuments.length;
      const indexedDocs = mockLocalDocuments.filter((d) => d.status === 'Indexed').length;
      const processingDocs = mockLocalDocuments.filter((d) => d.status === 'Processing').length;
      const errorDocs = mockLocalDocuments.filter((d) => d.status === 'Failed').length;
      const totalChunks = mockLocalDocuments.reduce((acc, d) => acc + (d.chunkCount || 0), 0);

      return {
        documents: totalDocs,
        indexed: indexedDocs,
        processing: processingDocs,
        chunks: totalChunks || MOCK_DASHBOARD_STATS.chunks,
        errors: errorDocs,
      };
    },
  },
};
