// src/components/documents/UploadDocumentModal.jsx
import React, { useState, useRef } from 'react';
import { UploadCloud, File, AlertCircle, CheckCircle2, Loader2, X } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';

export function UploadDocumentModal({ isOpen, onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [region, setRegion] = useState('India');
  const [category, setCategory] = useState('Leave Policy');
  const [version, setVersion] = useState('2026.1');
  const [effectiveDate, setEffectiveDate] = useState('2026-01-01');

  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStep, setUploadStep] = useState(''); // 'Uploading document...' | 'Extracting and indexing...'
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  const resetForm = () => {
    setFile(null);
    setName('');
    setRegion('India');
    setCategory('Leave Policy');
    setVersion('2026.1');
    setEffectiveDate('2026-01-01');
    setError(null);
    setUploading(false);
    setUploadStep('');
  };

  const handleClose = () => {
    if (uploading) return;
    resetForm();
    onClose();
  };

  const handleFileSelect = (selectedFile) => {
    setError(null);
    if (!selectedFile) return;

    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx'].includes(ext)) {
      setError('Only PDF (.pdf) and Word (.docx) documents are supported.');
      return;
    }

    if (selectedFile.size > 25 * 1024 * 1024) {
      setError('File size exceeds the 25 MB limit.');
      return;
    }

    setFile(selectedFile);
    if (!name) {
      // Auto-populate document name from clean file name
      const cleanName = selectedFile.name
        .replace(/\.[^/.]+$/, '')
        .replace(/[_-]+/g, ' ')
        .trim();
      setName(cleanName);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError('Please select a PDF or DOCX file to upload.');
      return;
    }

    if (!name.trim()) {
      setError('Document name is required.');
      return;
    }

    try {
      setUploading(true);
      setUploadStep('Uploading document payload...');

      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', name.trim());
      formData.append('region', region);
      formData.append('category', category);
      formData.append('version', version);
      formData.append('effectiveDate', effectiveDate);

      // Transition step message for clear UX
      setTimeout(() => {
        setUploadStep('Extracting text, chunking & indexing into ChromaDB...');
      }, 500);

      await onUploadSuccess(formData);

      handleClose();
    } catch (err) {
      setError(err.message || 'Failed to upload and index document.');
      setUploading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Upload HR Policy Document"
      subtitle="Index official HR documents into ChromaDB for semantic RAG search"
      maxWidth="max-w-xl"
      footer={
        <div className="flex items-center justify-end gap-2.5 w-full">
          <Button variant="outline" size="sm" onClick={handleClose} disabled={uploading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleSubmit}
            isLoading={uploading}
            disabled={!file || !name.trim() || uploading}
          >
            {uploading ? uploadStep || 'Processing...' : 'Upload & Index'}
          </Button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {/* File Dropzone */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Document File <span className="text-rose-500">*</span>
          </label>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              if (e.dataTransfer.files?.[0]) {
                handleFileSelect(e.dataTransfer.files[0]);
              }
            }}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
              dragOver
                ? 'border-blue-500 bg-blue-50/50'
                : file
                ? 'border-emerald-300 bg-emerald-50/30'
                : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFileSelect(e.target.files?.[0])}
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="hidden"
            />

            {file ? (
              <div className="flex items-center justify-between p-2 bg-white rounded-lg border border-emerald-200 shadow-2xs">
                <div className="flex items-center gap-2.5 text-left min-w-0">
                  <div className="w-8 h-8 rounded-md bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                    <File className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-slate-800 truncate">{file.name}</p>
                    <p className="text-[11px] text-slate-500">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                  }}
                  className="p-1 text-slate-400 hover:text-slate-600 rounded-md"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <UploadCloud className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-xs font-medium text-slate-700">
                  Click to browse or drag & drop HR document
                </p>
                <p className="text-[11px] text-slate-400 mt-1">Supported formats: PDF, DOCX (Max 25MB)</p>
              </div>
            )}
          </div>
        </div>

        {/* Metadata Fields */}
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Document Display Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. India Leave Policy 2026"
              className="w-full text-xs sm:text-sm px-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Region</label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full text-xs sm:text-sm px-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Global">Global</option>
                <option value="India">India</option>
                <option value="USA">USA</option>
                <option value="UK">UK</option>
                <option value="Europe">Europe</option>
                <option value="Singapore">Singapore</option>
                <option value="APAC">APAC</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full text-xs sm:text-sm px-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Leave Policy">Leave Policy</option>
                <option value="Handbook">Handbook</option>
                <option value="Benefits">Benefits</option>
                <option value="Compliance">Compliance</option>
                <option value="Workplace">Workplace</option>
                <option value="Expenses">Expenses</option>
                <option value="Legal">Legal</option>
                <option value="Contracts">Contracts</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Version</label>
              <input
                type="text"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                placeholder="2026.1"
                className="w-full text-xs sm:text-sm px-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Effective Date</label>
              <input
                type="date"
                value={effectiveDate}
                onChange={(e) => setEffectiveDate(e.target.value)}
                className="w-full text-xs sm:text-sm px-3 py-2 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {uploading && (
          <div className="p-3 bg-blue-50 border border-blue-100 rounded-lg flex items-center gap-3 text-xs text-blue-800">
            <Loader2 className="w-4 h-4 animate-spin text-blue-600 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="font-semibold">{uploadStep}</p>
              <p className="text-[11px] text-blue-600">Generating embeddings & storing vector embeddings...</p>
            </div>
          </div>
        )}
      </form>
    </Modal>
  );
}
