'use client';

import { FinanceCard } from '@/app/components/Card';
import Footer from '../components/Footer';
import { useEffect, useRef } from 'react';

const cards = [
  {
    title: "Audit Path Tracker",
    bg: "papers.svg",
    contentList: [
      "Reconstruct the history of entries and their justifications"
    ]
  },
  {
    title: "AI Risk Detector",
    bg: "institution.svg",
    contentList: [
      "Flag high-risk entries or anomalies based on patterns in financial behavior"
    ]
  },
  {
    title: "Smart Suggestions Engine",
    bg: "pc.svg",
    contentList: [
      "Recommend fixes and provides references to the exact AAOIFI clause involved"
    ]
  }
];

// Simple bar chart data
const barData = [65, 40, 70, 85, 60];
const barLabels = ['2020', '2021', '2022', '2023', '2024'];

export default function Auditors() {
  // Refs for simple DOM-based charts
  const barChartRef = useRef(null);
  const lineChartRef = useRef(null);

  return (
    <main className="min-h-screen w-full flex flex-col bg-[#f5efe0]">
      {/* Header */}
      <header className="bg-[#1a322a] text-white py-4">
        <div className="max-w-[1200px] mx-auto px-4 flex justify-between items-center">
          <div className="font-['Kyiv_Type_Sans'] font-bold text-xl">LFT</div>
          <nav className="flex space-x-8">
            <a href="/" className="font-['Kyiv_Type_Sans']">Home</a>
            <a href="#" className="font-['Kyiv_Type_Sans']">Services</a>
            <a href="#" className="font-['Kyiv_Type_Sans']">A & Q</a>
            <a href="#" className="font-['Kyiv_Type_Sans']">Contact us</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-[#1a322a] text-white relative">
        <div className="max-w-[1200px] mx-auto px-4 pt-12 pb-40">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-['Kyiv_Type_Sans'] font-bold text-3xl mb-2">Welcome Back !</h1>
            <p className="font-['Laila'] text-base">You can now try our core functionalities</p>
          </div>
        </div>
        
        {/* Hero Bottom Wave (curve down - green to cream) */}
        <div className="absolute bottom-0 left-0 w-full">
          <svg viewBox="0 0 1440 160" preserveAspectRatio="none" className="w-full h-auto" style={{ display: 'block' }}>
            <path
              d="M0,64 C288,128 480,0 720,64 C960,128 1152,32 1440,64 L1440,160 L0,160 Z"
              fill="#f5efe0"
            />
          </svg>
        </div>
      </section>
      
      {/* Content Section with cream background */}
      <section className="py-8 bg-[#f5efe0]">
        {/* Charts Section */}
        <div className="max-w-[1200px] mx-auto px-4 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Bar Chart */}
            <div className="bg-[#f5efe0] p-4 rounded-md border border-[#1a322a]/10">
              <div className="h-56" ref={barChartRef}>
                <div className="flex h-40 items-end space-x-3 mb-2">
                  {barData.map((value, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div
                        className="w-8 bg-[#1a322a] rounded-t-sm"
                        style={{ height: `${value}%` }}
                      ></div>
                    </div>
                  ))}
                </div>
                <div className="h-px bg-[#1a322a] w-full"></div>
                <div className="flex justify-between mt-2">
                  {barLabels.map((label, index) => (
                    <div key={index} className="text-xs text-[#1a322a]">
                      {label}
                    </div>
                  ))}
                </div>
                <p className="text-center mt-2 text-xs text-[#1a322a]">
                  AAOIFI alignment status with FAS
                </p>
              </div>
            </div>
            
            {/* Line Chart */}
            <div className="bg-[#f5efe0] p-4 rounded-md border border-[#1a322a]/10">
              <div className="h-56" ref={lineChartRef}>
                <div className="h-40 w-full relative">
                  {/* Background grid lines */}
                  <div className="absolute top-0 w-full h-px bg-[#1a322a]/10"></div>
                  <div className="absolute top-1/4 w-full h-px bg-[#1a322a]/10"></div>
                  <div className="absolute top-2/4 w-full h-px bg-[#1a322a]/10"></div>
                  <div className="absolute top-3/4 w-full h-px bg-[#1a322a]/10"></div>
                  <div className="absolute bottom-0 w-full h-px bg-[#1a322a]/10"></div>
                  
                  {/* Line chart */}
                  <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full">
                    <path
                      d="M10,60 C30,30 50,50 70,40 C90,30 95,60 95,60"
                      stroke="#1a322a"
                      strokeWidth="1.5"
                      fill="none"
                    />
                  </svg>
                </div>
                <div className="h-px bg-[#1a322a] w-full mt-2"></div>
                <div className="flex justify-between mt-2">
                  <span className="text-xs text-[#1a322a]">Jan</span>
                  <span className="text-xs text-[#1a322a]">Mar</span>
                  <span className="text-xs text-[#1a322a]">Jun</span>
                  <span className="text-xs text-[#1a322a]">Sep</span>
                  <span className="text-xs text-[#1a322a]">Dec</span>
                </div>
                <p className="text-center mt-2 text-xs text-[#1a322a]">
                  Monthly alignment status
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Cards Section - 2-1 layout */}
        <div className="max-w-[1200px] mx-auto px-4">
          {/* First row - 2 cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="flex justify-center">
              <FinanceCard {...cards[0]} />
            </div>
            <div className="flex justify-center">
              <FinanceCard {...cards[1]} />
            </div>
          </div>
          
          {/* Second row - 1 centered card */}
          <div className="flex justify-center mb-8">
            <div className="max-w-[374px] w-full">
              <FinanceCard {...cards[2]} />
            </div>
          </div>
        </div>
      </section>
      
      {/* Bottom Wave Section (cream to green) */}
      <section className="bg-[#1a322a] relative mt-8">
        <div className="h-30"></div>
        {/* Top Wave (curve up - cream to green) */}
        <div className="absolute top-0 left-0 w-full">
          <svg viewBox="0 0 1440 160" preserveAspectRatio="none" className="w-full h-auto" style={{ display: 'block', transform: 'rotate(180deg)' }}>
            <path
              d="M0,64 C288,128 480,0 720,64 C960,128 1152,32 1440,64 L1440,160 L0,160 Z"
              fill="#f5efe0"
            />
          </svg>
        </div>
      </section>
      
      <Footer/>
    </main>
  );
}