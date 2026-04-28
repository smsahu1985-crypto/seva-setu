import React from "react";
import { mockNeeds, URGENCY, CATEGORIES } from "../data/mockNeeds";
import { motion } from "framer-motion";


const getUrgencyStyles = (urgency) => {
  switch (urgency) {
    case URGENCY.CRITICAL:
      return "bg-red-100 text-red-800 border-red-200";
    case URGENCY.HIGH:
      return "bg-slate-100 text-slate-600 border-slate-200";
    case URGENCY.MEDIUM:
      return "bg-slate-100 text-slate-600 border-slate-200";
    case URGENCY.LOW:
      return "bg-slate-100 text-slate-600 border-slate-200";
    default:
      return "bg-slate-100 text-slate-600 border-slate-200";
  }
};

const ImpactStat = ({ label, value }) => (
  <div className="flex flex-col items-center md:items-start scale-90 md:scale-100">
    <span className="text-lg md:text-xl font-bold text-blue-700">{value}</span>
    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">{label}</span>
  </div>
);


const RoleCard = ({ title, description, icon, color, onClick }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ y: -5 }}
    whileTap={{ scale: 0.98 }}
    className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm hover:shadow-2xl hover:border-blue-500 transition-all duration-300 text-left group"
  >
    <div className={`w-16 h-16 ${color} rounded-2xl flex items-center justify-center text-3xl mb-6 group-hover:scale-110 transition-transform`}>
      {icon}
    </div>
    <h3 className="text-xl font-bold text-slate-900 mb-3">{title}</h3>
    <p className="text-slate-500 text-sm leading-relaxed">
      {description}
    </p>
    <div className="mt-6 flex items-center gap-2 text-blue-600 font-bold text-sm">
      Get Started
      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
      </svg>
    </div>
  </motion.button>
);


export default function Dashboard({ onNavigate }) {
  return (
    <div className="py-6 min-h-[85vh] flex flex-col justify-center">
      {/* Hero Section */}
      <header className="mb-8 text-center md:text-left">
        <div className="max-w-3xl">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight mb-4">
            Welcome to Seva Setu. <br />
            <span className="text-blue-600">How would you like to help today?</span>
          </h1>
          <p className="text-base text-slate-500 leading-relaxed font-normal mb-6">
            Seva Setu bridges the gap between scattered community reports and immediate NGO action. 
            Join our ecosystem to prioritize critical needs and ensure no cry for help goes unheard.
          </p>
        </div>

        {/* Live Impact Strip */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col md:flex-row justify-around gap-4 max-w-2xl">
          <ImpactStat label="Lives Impacted" value="1,200+" />
          <div className="hidden md:block w-px bg-slate-100 h-8" />
          <ImpactStat label="NGOs Verified" value="85" />
          <div className="hidden md:block w-px bg-slate-100 h-8" />
          <ImpactStat label="Resources Allocated" value="₹4.5L" />
        </div>
      </header>

      {/* Role Selection Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <RoleCard
          title="I Need Help"
          description="Report a community need, crisis, or resource shortage without an account. Our AI will route it to local heroes."
          icon="❤️"
          color="bg-red-50"
          onClick={() => onNavigate("report")}
        />
        <RoleCard
          title="I Want to Volunteer"
          description="Search for active missions, match your professional skills, and track your verified community impact."
          icon="👥"
          color="bg-blue-50"
          onClick={() => onNavigate("volunteer")}
        />
        <RoleCard
          title="NGO Command Center"
          description="Manage smart inventory, detect AI-clustered need hotspots, and coordinate volunteer response in real-time."
          icon="🏢"
          color="bg-slate-900 text-white"
          onClick={() => onNavigate("ngo")}
        />
      </div>
      
      {/* Footer Note */}
      <div className="text-center text-slate-400 text-sm">
        Trusted by 50+ local organizations and thousands of community members.
      </div>
    </div>
  );
}



