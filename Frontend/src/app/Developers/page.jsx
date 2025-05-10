'use client';

import { FinanceCard } from '@/app/components/Card';
import Footer from '../components/Footer';

const cards = [
  {
    title: "Simulation Engine",
    bg: "papers.svg",
    contentList: [
      "Creates interactive case studies or transaction scenarios for learners."
    ]
  },
  {
    title: "AI-Powered Learning Assistant",
    bg: "institution.svg",
    contentList: [
      "Answers student questions and explains accounting rules in context"
    ]
  },
  {
    title: "Assessment Generator",
    bg: "pc.svg",
    contentList: [
      "Builds quizzes/tests based on AAOIFI standards for classrooms or certifications"
    ]
  },
  {
    title: "Innovation Sandbox",
    bg: "pcandpapers.svg",
    contentList: [
      "A controlled environment where developers can test new Islamic financial products with built-in compliance checks"
    ]
  }
];

export default function Developers() {
  return (
    <main className="min-h-screen w-full flex flex-col">
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
      <section 
        className="bg-[#1a322a] text-white relative"
        style={{
          backgroundImage: "url('/Images/zakhraf.svg')",
          backgroundSize: 'cover',
          backgroundRepeat: 'repeat',
          backgroundPosition: 'center'
        }}
      >
        <div className="max-w-[1200px] mx-auto px-4 pt-12 pb-60">
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
      
      {/* Wave Section 1 (cream colored background) */}
      <section className="bg-[#f5efe0]">
        <div className="h-10"></div>
      </section>
      
      {/* Wave Section 2 (green colored, separating top cream section from bottom cream) */}
      <section className="bg-[#1a322a] relative">
        <div className="h-10"></div>
        {/* Top Wave (curve up - cream to green) */}
        <div className="absolute top-0 left-0 w-full">
          <svg viewBox="0 0 1440 160" preserveAspectRatio="none" className="w-full h-auto" style={{ display: 'block', transform: 'rotate(180deg)' }}>
            <path
              d="M0,64 C288,128 480,0 720,64 C960,128 1152,32 1440,64 L1440,160 L0,160 Z"
              fill="#f5efe0"
            />
          </svg>
        </div>
        
        {/* Bottom Wave (curve down - green to cream) */}
        <div className="absolute bottom-0 left-0 w-full">
          <svg viewBox="0 0 1440 160" preserveAspectRatio="none" className="w-full h-auto" style={{ display: 'block' }}>
            <path
              d="M0,64 C288,128 480,0 720,64 C960,128 1152,32 1440,64 L1440,160 L0,160 Z"
              fill="#f5efe0"
            />
          </svg>
        </div>
      </section>
      
      {/* Cards Section (cream background) */}
      <section className="bg-[#f5efe0] py-16">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {cards.map((card, idx) => (
              <div key={idx} className="flex justify-center">
                <FinanceCard {...card} />
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Wave Section 3 (green colored, before footer) */}
      <section className="bg-[#1a322a] relative">
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