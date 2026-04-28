import { useState } from "react";

const ROLE_LINKS = {
  public: [
    { label: "Dashboard", page: "dashboard" },
    { label: "Report Need", page: "report" },
  ],
  volunteer: [
    { label: "Find Missions", page: "volunteer" },
    { label: "My Portal", page: "volunteer-portal" },
  ],
  ngo: [
    { label: "NGO Dashboard", page: "ngo" },
    { label: "Inventory", page: "ngo" }, // In a real app these would be anchors or subpages
  ],
};

export default function Navbar({ currentPage, onNavigate }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleNavClick = (e, page) => {
    e.preventDefault();
    onNavigate(page);
    setMenuOpen(false);
  };

  return (
    <nav className="fixed top-0 z-50 w-full bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Back Button */}
          <div className="flex items-center gap-4">
            <a
              href="/"
              onClick={(e) => handleNavClick(e, "dashboard")}
              className="text-xl font-bold text-blue-700 tracking-tight select-none flex items-center gap-2"
            >
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-lg">S</div>
              <span className="hidden sm:inline">Seva Setu</span>
            </a>

            {currentPage !== "dashboard" && (
              <button
                onClick={() => onNavigate("dashboard")}
                className="flex items-center gap-1.5 text-sm font-bold text-slate-500 hover:text-blue-600 transition-colors pl-4 border-l border-slate-200"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M10 19l-7-7m0 0l-7-7m7-7" />
                </svg>
                Back to Home
              </button>
            )}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-6 mr-4">
              <a href="#about" className="text-sm font-medium text-slate-500 hover:text-slate-900">About</a>
              <a href="#impact" className="text-sm font-medium text-slate-500 hover:text-slate-900">Impact</a>
            </div>
            
            <button
              onClick={() => onNavigate("ngo")}
              className="hidden sm:inline-flex items-center px-4 py-2 text-sm font-bold text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              Admin Access
            </button>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 rounded-md text-slate-600"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Dropdown */}
      {menuOpen && (
        <div className="md:hidden bg-white border-t border-slate-100 p-4 space-y-3">
          <button onClick={() => { onNavigate("dashboard"); setMenuOpen(false); }} className="block w-full text-left text-sm font-bold text-slate-600">Home</button>
          <button onClick={() => { onNavigate("ngo"); setMenuOpen(false); }} className="block w-full text-left text-sm font-bold text-blue-600">Admin Access</button>
        </div>
      )}
    </nav>
  );
}



