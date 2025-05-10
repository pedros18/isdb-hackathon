import React from 'react';

export function Button({ children, className = '', ...props }) {
  return (
    <button 
      className={`px-5 py-2 rounded font-['Jost'] text-sm ${className}`} 
      {...props}
    >
      {children}
    </button>
  );
}