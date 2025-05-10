'use client';

import { FinanceCard } from '@/app/components/Card';
import Footer from '../components/Footer';
import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';

const cards = [
  {
    title: "Centralized Oversight Platform",
    bg: "papers.svg",
    contentList: [
      "View and manage compliance metrics across all regulated institutions."
    ]
  },
  {
    title: "Institution Scoring Engine",
    bg: "institution.svg",
    contentList: [
      "Grade each institution based on adherence to AAOIFI standards."
    ]
  },
  {
    title: "Smart Suggestions Engine",
    bg: "pc.svg",
    contentList: [
      "Recommend fixes and provides references to the exact AAOIFI clause involved"
    ]
  },
  {
    title: "Systemic Risk Analyzer",
    bg: "pcandpapers.svg",
    contentList: [
      "Detect emerging risks threatening industry-wide compliance flux"
    ]
  }
];

export default function Regulators() {
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [chartData, setChartData] = useState(null);
  
  const fileInputRef = useRef(null);
  const barChartRef = useRef(null);
  const lineChartRef = useRef(null);
  
  const handleFileUpload = async () => {
    if (!selectedFile) return;
    
    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await axios.post('http://localhost:8000/api/analyze-standard', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setAnalysisResults(response.data);
      
      if (response.data.chart_data) {
        setChartData(response.data.chart_data);
      }
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmitFeedback = async () => {
    if (!analysisResults || !feedback) return;
    
    try {
      const response = await axios.post('http://localhost:8000/api/submit-feedback', {
        feedback,
        standard_name: analysisResults.standard_name,
      });
      
      setAnalysisResults(prev => ({
        ...prev,
        feedback: response.data
      }));
      setFeedback('');
    } catch (error) {
      console.error('Feedback submission error:', error);
    }
  };
  
  useEffect(() => {
    if (!chartData || !barChartRef.current || !lineChartRef.current) return;
    
    if (barChartRef.current.chart) {
      barChartRef.current.chart.destroy();
    }
    if (lineChartRef.current.chart) {
      lineChartRef.current.chart.destroy();
    }
    
    const barCtx = barChartRef.current.getContext('2d');
    barChartRef.current.chart = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: chartData.categories.labels,
        datasets: [{
          label: 'Compliance Score by Category',
          data: chartData.categories.data,
          backgroundColor: [
            'rgba(26, 50, 42, 0.7)',
            'rgba(58, 106, 90, 0.7)',
            'rgba(90, 162, 132, 0.7)',
            'rgba(122, 218, 174, 0.7)',
            'rgba(154, 255, 216, 0.7)',
          ],
          borderColor: [
            'rgba(26, 50, 42, 1)',
            'rgba(58, 106, 90, 1)',
            'rgba(90, 162, 132, 1)',
            'rgba(122, 218, 174, 1)',
            'rgba(154, 255, 216, 1)',
          ],
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
    
    const lineCtx = lineChartRef.current.getContext('2d');
    lineChartRef.current.chart = new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: chartData.time_series.labels,
        datasets: [{
          label: 'Compliance Score Trend',
          data: chartData.time_series.data,
          fill: false,
          backgroundColor: 'rgba(26, 50, 42, 0.2)',
          borderColor: 'rgba(26, 50, 42, 1)',
          tension: 0.1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
  }, [chartData]);

  return (
    <main className="min-h-screen w-full flex flex-col bg-[#f5efe0]">
      {/* Header Section */}
      <header className="bg-[#1a322a] py-4">
        <div className="max-w-[1200px] mx-auto px-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <div className="font-['Kyiv_Type_Sans'] text-white text-xl font-bold">FenNex</div>
              <div className="hidden md:flex gap-6">
                <a href="#" className="text-white hover:text-[#c5d6d0] transition">Features</a>
                <a href="#" className="text-white hover:text-[#c5d6d0] transition">Solutions</a>
                <a href="#" className="text-white hover:text-[#c5d6d0] transition">About</a>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button className="text-white bg-[#3a6a5a] hover:bg-[#4a7a6a] transition px-4 py-2 rounded">
                Contact Us
              </button>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-[#1a322a] pb-12 pt-6">
        <div className="max-w-[1200px] mx-auto px-4">
          <div className="flex flex-col items-center text-center">
            <h1 className="text-3xl md:text-4xl lg:text-5xl text-white font-['Kyiv_Type_Sans'] font-bold">
              Regulatory Excellence Platform
            </h1>
            <p className="text-[#c5d6d0] mt-4 text-lg font-['Laila'] max-w-2xl">
              Comprehensive tools for Islamic finance regulators to monitor compliance, 
              analyze standards, and optimize regulatory frameworks.
            </p>
            <div className="mt-8">
              <button className="bg-white text-[#1a322a] hover:bg-[#f0f0f0] transition px-6 py-3 rounded font-bold">
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards Section - Centered */}
      <section className="py-12">
        <div className="max-w-[1200px] mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-['Kyiv_Type_Sans'] font-bold text-center text-[#1a322a] mb-8">
            Built for Regulatory Excellence
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {cards.map((card, index) => (
              <FinanceCard
                key={index}
                title={card.title}
                bg={card.bg}
                contentList={card.contentList}
              />
            ))}
          </div>
        </div>
      </section>
      
      {/* File Upload Section */}
      <section className="max-w-[1200px] mx-auto px-4 py-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="font-['Kyiv_Type_Sans'] text-xl mb-4 text-[#1a322a]">
            Analyze AAOIFI Standard
          </h2>
          
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                accept=".pdf"
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full bg-[#1a322a] text-white py-2 px-4 rounded hover:bg-[#2a4a3a] transition"
              >
                {selectedFile ? selectedFile.name : 'Select PDF File'}
              </button>
            </div>
            <button
              onClick={handleFileUpload}
              disabled={!selectedFile || isAnalyzing}
              className="bg-[#3a6a5a] text-white py-2 px-6 rounded hover:bg-[#4a7a6a] transition disabled:opacity-50"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </section>
      
      {/* Chart Data Section */}
      {chartData && (
        <section className="max-w-[1200px] mx-auto px-4 py-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="font-['Kyiv_Type_Sans'] text-xl mb-4 text-[#1a322a]">
              Compliance Analytics
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-['Kyiv_Type_Sans'] font-bold mb-2">Compliance by Category</h3>
                <div className="bg-[#f5f5f5] p-4 rounded">
                  <canvas ref={barChartRef}></canvas>
                </div>
              </div>
              <div>
                <h3 className="font-['Kyiv_Type_Sans'] font-bold mb-2">Compliance Trend</h3>
                <div className="bg-[#f5f5f5] p-4 rounded">
                  <canvas ref={lineChartRef}></canvas>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
      
      {/* Analysis Results Section */}
      {analysisResults && (
        <section className="max-w-[1200px] mx-auto px-4 py-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="font-['Kyiv_Type_Sans'] text-xl mb-4 text-[#1a322a]">
              Analysis Results: {analysisResults.standard_name}
            </h2>
            
            <div className="mb-6 p-4 bg-[#f5f5f5] rounded text-black">
              <h3 className="font-['Kyiv_Type_Sans'] font-bold mb-2">Executive Summary</h3>
              <p className="font-['Laila']">
                {analysisResults.report?.executive_summary || 'No summary available'}
              </p>
            </div>
            
            <div className="mb-6 text-black">
              <h3 className="font-['Kyiv_Type_Sans'] font-bold mb-2">Enhancement Recommendations</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysisResults.enhancement && (
                  <>
                    <div className="p-4 bg-[#f0f7f4] rounded">
                      <h4 className="font-['Kyiv_Type_Sans'] font-bold">Clarity Improvements</h4>
                      <p className="font-['Laila']">
                        {analysisResults.enhancement.clarity_improvements}
                      </p>
                    </div>
                    <div className="p-4 bg-[#f0f7f4] rounded">
                      <h4 className="font-['Kyiv_Type_Sans'] font-bold">Modern Adaptations</h4>
                      <p className="font-['Laila']">
                        {analysisResults.enhancement.modern_adaptations}
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
            
            <div className="mt-6 text-black">
              <h3 className="font-['Kyiv_Type_Sans'] font-bold mb-2">Provide Feedback</h3>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                className="w-full p-3 border rounded mb-2 text-black"
                rows={4}
                placeholder="Enter your feedback on these recommendations..."
              />
              <button
                onClick={handleSubmitFeedback}
                disabled={!feedback}
                className="bg-[#1a322a] text-white py-2 px-6 rounded hover:bg-[#2a4a3a] transition disabled:opacity-50"
              >
                Submit Feedback
              </button>
            </div>
            
            {analysisResults.feedback && (
              <div className="mt-6 p-4 bg-[#f5f5f5] rounded text-black">
                <h3 className="font-['Kyiv_Type_Sans'] font-bold mb-2">Feedback Response</h3>
                <p className="font-['Laila']">
                  {analysisResults.feedback.recommended_refinements}
                </p>
              </div>
            )}
          </div>
        </section>
      )}
      
      <Footer />
    </main>
  );
}
