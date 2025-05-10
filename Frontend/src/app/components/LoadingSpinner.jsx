// app/components/LoadingSpinner.tsx
'use client';

export default function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#1a322a]"></div>
    </div>
  );
}