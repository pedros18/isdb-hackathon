export default function Footer() {
  return (
    <footer className="bg-[#1a322a] text-white pt-12 pb-5">
      <div className="max-w-[1200px] mx-auto px-4">
        {/* Responsive grid: 1 col on mobile, 2 on sm, 4 on lg */}
        <div className="grid grid-cols-3 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Product */}
          <div >
            <h3 className="font-['Kyiv_Type_Sans'] text-[#c2a87d] text-sm mb-4">Product</h3>
            <ul className="space-y-2">
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">Features</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">How it works</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">Pricing</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">Testimonials</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">FAQ</a></li>
            </ul>
          </div>
          {/* Information */}
          <div>
            <h3 className="font-['Kyiv_Type_Sans'] text-[#c2a87d] text-sm mb-4">Information</h3>
            <ul className="space-y-2">
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">FAQ</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">Blog</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">Support</a></li>
            </ul>
          </div>
          {/* Company */}
          <div>
            <h3 className="font-['Kyiv_Type_Sans'] text-[#c2a87d] text-sm mb-4">Company</h3>
            <ul className="space-y-2">
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">About us</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">Careers</a></li>
              <li><a href="#" className="font-['Laila'] text-xs opacity-75">Contact us</a></li>
            </ul>
          </div>
          {/* Subscribe */}
          <div>
            <h3 className="font-['Kyiv_Type_Sans'] text-[#c2a87d] text-sm mb-4">Subscribe</h3>
            <form className="flex flex-col sm:flex-row gap-2">
              <input 
                type="email" 
                className="py-1.5 px-2 rounded w-full text-sm text-black" 
                placeholder="Email address"
              />
              <button className="bg-[#c2a87d] px-3 rounded text-[#1a322a] w-[100px] sm:w-auto">
                →
              </button>
            </form>
            <p className="font-['Laila'] text-xs opacity-60 mt-3">
              Hello, we are Lift Media. Our goal is to translate the positive effects from revolutionizing how companies engage with their clients & their team.
            </p>
          </div>
        </div>
        {/* Bottom row */}
        <div className="flex flex-col md:flex-row justify-between items-center border-t border-gray-700/20 mt-10 pt-5 gap-4">
          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-5">
            <span className="font-['Laila'] text-xs">Terms</span>
            <span className="font-['Laila'] text-xs">Privacy</span>
            <span className="font-['Laila'] text-xs">Cookies</span>
          </div>
          <div className="font-['Laila'] text-xs text-center">
            © 2025 FEN
          </div>
          <div className="flex space-x-3">
            <a href="#" className="w-8 h-8 rounded-full border border-white/25 flex items-center justify-center" aria-label="Twitter">•</a>
            <a href="#" className="w-8 h-8 rounded-full border border-white/25 flex items-center justify-center" aria-label="Facebook">•</a>
            <a href="#" className="w-8 h-8 rounded-full border border-white/25 flex items-center justify-center" aria-label="Instagram">•</a>
          </div>
        </div>
      </div>
    </footer>
  );
}