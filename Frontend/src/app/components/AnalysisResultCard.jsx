// app/components/AnalysisResultCard.tsx
'use client';

import { useState } from 'react';

export default function AnalysisResultCard({ 
  title, 
  content,
  defaultCollapsed = false 
}) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  
  return (
    <div className="mb-4 border rounded-lg overflow-hidden">
      <button
        className="w-full text-left p-4 bg-[#1a322a] text-white font-['Kyiv_Type_Sans'] flex justify-between items-center"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <span>{title}</span>
        <span>{isCollapsed ? '+' : '-'}</span>
      </button>
      
      {!isCollapsed && (
        <div className="p-4 bg-white">
          <pre className="whitespace-pre-wrap font-['Laila'] text-sm">{content}</pre>
        </div>
      )}
    </div>
  );
}