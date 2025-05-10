import { FinanceCard } from '@/app/components/Card';
import Footer from '@/app/components/Footer';
export default function Home() {
  // Card data (use the icon as the background image)
  const cards = [
    {
      title: "Financial Institutions",
      bg: "institution.svg",
      subtitle: "Automate compliance, reduce risk",
      contentList: [
        "Instantly classify transactions and apply the right AAOIFI standards",
        "Generate journal entries and reports with built-in validation."
      ],
      link: "/FinancialInstitutions"
    },
    {
      title: "Compliance Officers",
      bg: "papers.svg",
      subtitle: "Smarter audits, stronger oversight.",
      contentList: [
        "Detect anomalies and verify treatment accuracy automatically",
        "Trace every entry back to its justification and standard reference."
      ],
      link: "/Auditors"
    },
    {
      title: "Regulators",
      bg: "pc.svg",
      subtitle: "Automate compliance, reduce risk",
      contentList: [
        "Monitor institutions' adherence to AAOIFI standards in real time.",
        "Receive alerts on violations and systemic risk indicators."
      ],
      link: "/Regulators"
    },
    {
      title: "Developers & Educators",
      bg: "pcandpapers.svg",
      subtitle: "Build, teach, innovate with AAOIFI",
      contentList: [
        "Access AAOIFI APIs, simulators, and AI training assistants.",
        "Create learning modules and test products in a sandbox."
      ],
      link: "/Developers"
    }
  ];

  return (
    <main className="min-h-screen bg-[#f5efe0]">
      {/* Header */}
      <header className="bg-[#1a322a] text-white py-4">
      <div className="max-w-[1200px] mx-auto px-4 flex justify-between items-center">
  <div className="font-['Kyiv_Type_Sans'] font-extrabold text-5xl leading-none tracking-[0%] w-[169px] h-[59px] py-3 pl-10">
    LFT
  </div>
  <nav className="flex space-x-8">
    <a href="#" className="font-['Kyiv_Type_Sans']">Home</a>
    <a href="#" className="font-['Kyiv_Type_Sans']">Services</a>
    <a href="#" className="font-['Kyiv_Type_Sans']">A & Q</a>
    <a href="#" className="font-['Kyiv_Type_Sans']">Contact us</a>
  </nav>
</div>
      </header>
      
      {/* Hero Section */}
      <section className="bg-[#1a322a] text-white relative">
        <div className="max-w-[1200px] mx-auto px-4 pt-16 pb-40">
          <div className="max-w-3xl">
            <h1 className="font-['jost'] font-bold text-3xl mb-3">
              AI-Driven Compliance & Innovation for Islamic Finance
            </h1>
            <p className="font-['Laila'] text-base mb-8">
              An intelligent platform simplifying the adoption of AAOIFI standards for banks, 
              auditors, regulators, and fintech innovators.
            </p>
            <div className="flex space-x-4">
              <button className="bg-[#c2a87d] text-[#1a322a] px-6 py-2 rounded font-medium">
                See how it works
              </button>
              <button className="border border-[#c2a87d] text-[#c2a87d] px-6 py-2 rounded font-medium">
                Request a demo
              </button>
            </div>
          </div>
        </div>
        {/* Top Wave */}
        <div className="absolute bottom-0 left-0 w-full">
          <svg viewBox="0 0 1440 160" preserveAspectRatio="none" className="w-full h-auto" style={{ display: 'block' }}>
            <path
              d="M0,64 C288,128 480,0 720,64 C960,128 1152,32 1440,64 L1440,160 L0,160 Z"
              fill="#f5efe0"
            />
          </svg>
        </div>
      </section>
      
      {/* Main Content */}
      <section className="py-16">
  <div className="max-w-7xl mx-auto mb-16 px-4">
  <p
  className="mb-6 font-['Jost'] text-[#1a322a] text-justify leading-relaxed"
  style={{
    fontWeight: 700,
    fontSize: 'clamp(18px, 3vw, 28px)',
    lineHeight: '145%',
    letterSpacing: 0,
  }}
>
  The adoption of AAOIFI standards remains a complex and time-consuming challenge for many Islamic financial institutions, auditors, and regulators. Manual interpretation of accounting treatments, evolving compliance requirements, and a lack of accessible training tools often lead to inefficiencies and inconsistencies.
  <br /><br />
  Our AI-powered platform bridges this gap by delivering smart automation, real-time compliance validation, intelligent audit assistance, and interactive educational tools — all designed to simplify, standardize, and accelerate the implementation of AAOIFI standards across the Islamic finance ecosystem.
</p>
  </div>
  <div className="flex justify-center">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-20">
            {cards.map((card, idx) => (
              <div key={idx} className="flex justify-center">
                <FinanceCard {...card} />
              </div>
            ))}
          </div>
        </div>
</section>
      
      {/* Bottom Wave */}
      <div className="bg-[#1a322a] w-full">
        <svg 
          viewBox="0 0 1440 120" 
          preserveAspectRatio="none" 
          className="w-full" 
          style={{ display: 'block', marginBottom: -1 }}
        >
          <path
            d="M0,0 C320,64 480,16 720,48 C960,80 1120,16 1440,32 L1440,120 L0,120 Z"
            fill="#f5efe0"
            transform="rotate(180) translate(-1440, -120)"
          />
        </svg>
      </div>
      
      {/* Footer */}
     <Footer/>
    </main>
  );
}