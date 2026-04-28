import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { mockNeeds, URGENCY } from "../data/mockNeeds";


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

const NeedCard = ({ need }) => {
  const progress = (need.volunteersAssigned / need.volunteersNeeded) * 100;
  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm hover:shadow-xl hover:border-blue-500 hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col group">
      <div className="flex items-center gap-3 mb-4">
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${getUrgencyStyles(need.urgency)}`}>
          {need.urgency}
        </span>
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          {need.category}
        </span>
      </div>
      <h3 className="text-lg font-bold text-slate-800 mb-2 group-hover:text-blue-700 transition-colors line-clamp-2">
        {need.title}
      </h3>
      <div className="flex items-center text-xs text-slate-500 mb-6">
        <svg className="flex-shrink-0 mr-1.5 h-3.5 w-3.5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        </svg>
        {need.location.city}
      </div>
      <div className="mt-auto pt-4 border-t border-slate-50">
        <div className="flex justify-between text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">
          <span>Match</span>
          <span className="text-blue-600">{need.volunteersAssigned}/{need.volunteersNeeded}</span>
        </div>
        <div className="w-full bg-slate-100 rounded-full h-1 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${progress >= 100 ? 'bg-green-500' : 'bg-blue-600'}`}
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

const ProofOfWorkModal = ({ isOpen, onClose, taskTitle }) => (
  <AnimatePresence>
    {isOpen && (
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
        >
          <div className="p-6 border-b border-slate-100">
            <div className="flex justify-between items-center mb-1">
              <h3 className="text-xl font-bold text-slate-900">Proof of Work</h3>
              <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p className="text-sm text-slate-500">Verifying: {taskTitle}</p>
          </div>
          <div className="p-6 space-y-6">
            <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center hover:border-blue-400 transition-colors cursor-pointer group">
              <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform text-blue-600 text-2xl">📸</div>
              <p className="text-sm font-bold text-slate-700">Upload Geotagged Photo</p>
              <p className="text-xs text-slate-400 mt-1">AI will verify location & activity</p>
            </div>
          </div>
          <div className="p-6 bg-slate-50 border-t border-slate-100 flex gap-3">
            <button onClick={onClose} className="flex-1 py-2 text-slate-600 font-bold text-sm hover:bg-slate-200 rounded-lg transition-colors">Cancel</button>
            <button onClick={() => { alert("Proof of Work Submitted!"); onClose(); }} className="flex-1 py-2 bg-green-600 text-white font-bold text-sm hover:bg-green-700 rounded-lg transition-colors">Submit Verification</button>
          </div>
        </motion.div>
      </div>
    )}
  </AnimatePresence>
);

export default function VolunteerPortal() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState("");

  return (
    <div className="py-8 space-y-12">
      {/* Header & Stats */}
      <div className="flex flex-col lg:flex-row justify-between items-start gap-8">
        <div className="max-w-xl">
          <h1 className="text-3xl font-bold text-slate-900 mb-3 tracking-tight">Volunteer Portal</h1>
          <p className="text-slate-500 leading-relaxed">
            Welcome back, Ananya! You are currently <span className="text-blue-600 font-bold underline">Level 4</span>. 
            Your contributions have impacted over 120 lives this month.
          </p>
        </div>
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex items-center gap-6 min-w-[320px]">
          <div className="flex flex-col items-center">
            <div className="text-2xl font-bold text-blue-600">85%</div>
            <div className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Reliability</div>
          </div>
          <div className="flex-1 space-y-2">
            <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
              <motion.div initial={{ width: 0 }} animate={{ width: "85%" }} className="bg-blue-600 h-full" />
            </div>
            <div className="flex justify-between text-[10px] font-bold text-slate-500">
              <span>Lvl 4</span>
              <span>Next: Lvl 5 (150xp)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommended Section */}
      <section>
        <div className="flex items-center gap-2 mb-6">
          <div className="w-2 h-8 bg-blue-600 rounded-full" />
          <h2 className="text-xl font-bold text-slate-900">Recommended for Your Skills</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-50 p-6 rounded-3xl border border-blue-100 flex justify-between items-center group cursor-pointer hover:bg-blue-100 transition-colors">
            <div>
              <div className="text-[10px] font-bold text-blue-500 uppercase mb-1 tracking-widest">Top Match (Medical)</div>
              <h3 className="font-bold text-slate-800">First Aid Assistance - Wardha</h3>
            </div>
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-blue-600 group-hover:translate-x-1 transition-transform">→</div>
          </div>
          <div className="bg-green-50 p-6 rounded-3xl border border-green-100 flex justify-between items-center group cursor-pointer hover:bg-green-100 transition-colors">
            <div>
              <div className="text-[10px] font-bold text-green-600 uppercase mb-1 tracking-widest">High Impact (Logistics)</div>
              <h3 className="font-bold text-slate-800">Ration Distribution - Nagpur</h3>
            </div>
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-green-600 group-hover:translate-x-1 transition-transform">→</div>
          </div>
        </div>
      </section>

      {/* Omni-Search & Filters */}
      <section className="space-y-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 relative">
            <input
              type="text"
              className="w-full pl-12 pr-4 py-4 bg-white rounded-2xl shadow-md border-none focus:ring-2 focus:ring-blue-500 transition-all placeholder-slate-400 text-slate-700"
              placeholder="Search by city, pincode, or NGO name..."
            />
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">🔍</div>
          </div>
          <div className="flex flex-wrap gap-2">
            <select className="px-4 py-4 bg-white rounded-2xl shadow-md border-none text-xs font-bold text-slate-600 cursor-pointer">
              <option>Distance: Any</option>
              <option>Within 10km</option>
            </select>
            <select className="px-4 py-4 bg-white rounded-2xl shadow-md border-none text-xs font-bold text-slate-600 cursor-pointer">
              <option>Skill: Medical</option>
              <option>Skill: Logistics</option>
            </select>
            <select className="px-4 py-4 bg-white rounded-2xl shadow-md border-none text-xs font-bold text-slate-600 cursor-pointer">
              <option>Urgency: High</option>
              <option>Urgency: Critical</option>
            </select>
          </div>
        </div>

        {/* The Grid of Needs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
          {mockNeeds.map((need) => (
            <NeedCard key={need.id} need={need} />
          ))}
        </div>
      </section>

      <ProofOfWorkModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        taskTitle={selectedTask}
      />
    </div>
  );
}

