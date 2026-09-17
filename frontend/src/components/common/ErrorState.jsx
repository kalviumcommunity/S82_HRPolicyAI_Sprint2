// src/components/common/ErrorState.jsx
import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export function ErrorState({
  title = 'Something went wrong',
  message = 'An unexpected error occurred while communicating with the service.',
  onRetry,
  className = '',
}) {
  return (
    <div className={`p-6 bg-rose-50 border border-rose-200 rounded-xl text-center sm:text-left flex flex-col sm:flex-row items-center gap-4 ${className}`}>
      <div className="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 shrink-0">
        <AlertCircle className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-rose-900">{title}</h4>
        <p className="text-xs text-rose-700 mt-0.5">{message}</p>
      </div>
      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          icon={RefreshCw}
          className="bg-white border-rose-200 text-rose-700 hover:bg-rose-50 shrink-0"
        >
          Try Again
        </Button>
      )}
    </div>
  );
}
