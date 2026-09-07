// src/pages/Documents.jsx
import React, { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Filter,
  Plus,
  RefreshCw,
  SlidersHorizontal,
  X,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { DocumentTable } from '../components/documents/DocumentTable';
import { UploadDocumentModal } from '../components/documents/UploadDocumentModal';
import { Loading } from '../components/common/Loading';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { Button } from '../components/common/Button';
import { api } from '../services/api';

export function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [search, setSearch] = useState('');
  const [region, setRegion] = useState('All');
  const [category, setCategory] = useState('All');
  const [status, setStatus] = useState('All');

  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.documents.getAll({
        search,
        region,
        category,
        status,
      });
      setDocuments(data || []);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError(err.message || 'Unable to retrieve documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [region, category, status]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadDocuments();
  };

  const handleClearFilters = () => {
    setSearch('');
    setRegion('All');
    setCategory('All');
    setStatus('All');
  };

  const handleUploadSuccess = async (formData) => {
    await api.documents.upload(formData);
    await loadDocuments();
  };

  const handleDelete = async (id) => {
    try {
      await api.documents.delete(id);
      await loadDocuments();
    } catch (err) {
      console.error('Failed to delete document:', err);
      alert('Failed to delete document.');
    }
  };

  const handleReindex = async (id) => {
    try {
      await api.documents.reindex(id);
      await loadDocuments();
    } catch (err) {
      console.error('Failed to reindex document:', err);
      alert('Failed to re-index document.');
    }
  };

  const hasActiveFilters =
    search.trim() !== '' || region !== 'All' || category !== 'All' || status !== 'All';

  return (
    <PageContainer
      title="Policy Document Management"
      subtitle="Upload, re-index, and manage enterprise policy documents for semantic search"
    >
      <div className="space-y-6">
        {/* Top bar with Upload action */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Document Repository</h2>
            <p className="text-xs text-slate-500">
              Manage internal documents ingested into the RAG vector pipeline
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={RefreshCw}
              onClick={loadDocuments}
              title="Refresh repository"
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Plus}
              onClick={() => setIsUploadOpen(true)}
            >
              Upload Document
            </Button>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs space-y-3">
          <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-2.5">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Search className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by document title, filename, or topic..."
                className="w-full text-xs sm:text-sm pl-9 pr-4 py-2 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
              />
            </div>
            <Button type="submit" variant="secondary" size="sm">
              Search
            </Button>
          </form>

          {/* Dropdown Filters */}
          <div className="flex flex-wrap items-center gap-2.5 pt-2 border-t border-slate-100 text-xs">
            <div className="flex items-center gap-1.5 text-slate-500 font-medium">
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Filters:</span>
            </div>

            {/* Region Filter */}
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="All">All Regions</option>
              <option value="India">India</option>
              <option value="USA">USA</option>
              <option value="UK">UK</option>
              <option value="Europe">Europe</option>
              <option value="Singapore">Singapore</option>
              <option value="APAC">APAC</option>
              <option value="Global">Global</option>
            </select>

            {/* Category Filter */}
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="All">All Categories</option>
              <option value="Leave Policy">Leave Policy</option>
              <option value="Handbook">Handbook</option>
              <option value="Benefits">Benefits</option>
              <option value="Compliance">Compliance</option>
              <option value="Workplace">Workplace</option>
              <option value="Expenses">Expenses</option>
              <option value="Legal">Legal</option>
              <option value="Contracts">Contracts</option>
            </select>

            {/* Status Filter */}
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="All">All Statuses</option>
              <option value="Indexed">Indexed</option>
              <option value="Processing">Processing</option>
              <option value="Failed">Failed</option>
            </select>

            {hasActiveFilters && (
              <button
                type="button"
                onClick={handleClearFilters}
                className="flex items-center gap-1 text-slate-500 hover:text-rose-600 px-2 py-1 rounded hover:bg-slate-100 transition-colors ml-auto cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
                <span>Reset Filters</span>
              </button>
            )}
          </div>
        </div>

        {/* Content list */}
        {loading ? (
          <Loading message="Filtering document repository..." className="py-16" />
        ) : error ? (
          <ErrorState
            title="Failed to load documents"
            message={error}
            onRetry={loadDocuments}
          />
        ) : documents.length === 0 ? (
          <EmptyState
            title="No policy documents found"
            description={
              hasActiveFilters
                ? 'No documents matched the applied filters. Try clearing your search or filter criteria.'
                : 'Your knowledge base is empty. Upload your first HR policy document.'
            }
            icon={FileText}
            actionLabel="Upload HR Document"
            onAction={() => setIsUploadOpen(true)}
          />
        ) : (
          <DocumentTable
            documents={documents}
            onDelete={handleDelete}
            onReindex={handleReindex}
          />
        )}
      </div>

      {/* Upload Modal */}
      <UploadDocumentModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </PageContainer>
  );
}
