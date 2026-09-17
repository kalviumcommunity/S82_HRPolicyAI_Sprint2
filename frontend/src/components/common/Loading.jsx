// src/components/common/Loading.jsx
import React from 'react';
import { Loader2 } from 'lucide-react';

export function Loading({ message = 'Loading...', size = 'md', className = '' }) {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-7 h-7',
    lg: 'w-10 h-10',
  };

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-slate-500 ${className}`}>
      <Loader2 className={`${sizeMap[size] || sizeMap.md} animate-spin text-blue-600 mb-3`} />
      <p className="text-sm font-medium text-slate-600 animate-pulse">{message}</p>
    </div>
  );
}
