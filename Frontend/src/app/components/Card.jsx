'use client';

import Image from 'next/image';
import Link from 'next/link';
export function FinanceCard({
  title,
  bg,
  subtitle,
  contentList,
  link
}) {
  return (
    <div className="relative w-[374px] h-[319px] rounded-2xl shadow-xl overflow-hidden flex items-stretch"
         style={{
           boxShadow: '0 0 20px 0 #bdbda7',
           border: 'none',
           background: '#1a322a',
         }}>
      {/* Background image */}
      <Image
        src={`/Images/${bg}`}
        alt="Card background"
        fill
        className="object-cover"
        style={{ zIndex: 1 }}
        priority
      />
      {/* Overlay */}
      <div className="absolute inset-0 bg-[#0F3428] opacity-[0.79] z-10" />
      {/* Content */}
      <div className="relative z-20 flex flex-col h-full w-full px-7 py-6 text-white">
        {/* Title */}
        <h3 className="text-2xl font-extrabold font-['KyivType_Sans'] text-center mb-2 leading-tight">
          {title}
        </h3>
        {/* Subtitle */}
        {subtitle && (
          <p className="text-lg font-['Laila'] text-center mb-4">{subtitle}</p>
        )}
        {/* List */}
        <ul className="text-lg font-['Laila'] font-semibold space-y-3 mb-4">
          {contentList.map((item, idx) => (
            <li key={idx} className="flex items-start">
              <span className="mr-2">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
        {/* Button */}
        {link ? (
          <Link href={link} className="w-[80px] bg-[#c2a87d] text-[#1a322a] px-4 py-2 rounded-full text-sm font-medium hover:bg-[#d8c095] transition-colors">
            Try it
          </Link>
        ) : (
          <button className="mt-auto bg-[#a48c5c] text-white font-bold font-['KyivType_Sans'] text-xl rounded-full px-8 py-2 shadow">
            Try it
          </button>
        )}
      </div>
    </div>
  );
} 