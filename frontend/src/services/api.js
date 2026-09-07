// src/services/api.js
import {
  MOCK_USERS,
  MOCK_DOCUMENTS,
  MOCK_DASHBOARD_STATS,
  MOCK_CONVERSATIONS,
  MOCK_QA_DATABASE,
} from '../data/mockData';

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// If VITE_USE_MOCK_API is explicitly 'false', then use real network calls; otherwise default to mock mode.
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API !== 'false';

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

  // If not FormData, default to application/json
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
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

      // Simple mock password validation
      if (password && password.length < 4) {
        throw new Error('Password must be at least 4 characters long.');
      }

      const token = `mock_jwt_token_${user.id}_${Date.now()}`;
      return {
        token,
        user,
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
