import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { mockNeeds, URGENCY } from "../data/mockNeeds";

const calculateDeadline = (reportedAt, urgency) => {
  const start = new Date(reportedAt);
  const days = urgency === URGENCY.CRITICAL ? 1 : urgency === URGENCY.HIGH ? 3 : 7;
  return new Date(start.getTime() + days * 24 * 60 * 60 * 1000);
};

const getTimeRemaining = (deadline) => {
  const total = deadline.getTime() - new Date().getTime();
  const hours = Math.max(0, Math.floor(total / (1000 * 60 * 60)));
  const days = Math.floor(hours / 24);
  return { total, days, hours: hours % 24 };
};

const SidebarItem = ({ label, icon, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${active
        ? "bg-blue-50 text-blue-700 shadow-sm"
        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
      }`}
  >
    <span className="text-xl">{icon}</span>
    <span className="font-medium text-sm">{label}</span>
  </button>
);

const InventoryCard = ({ title, level, icon }) => (
  <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
    <div className="flex justify-between items-start mb-4">
      <div className="p-2 bg-slate-50 rounded-lg text-2xl">{icon}</div>
      <span className="px-2 py-1 bg-green-50 text-green-600 text-[10px] font-bold uppercase rounded border border-green-100">
        Auto-Deduct
      </span>
    </div>
    <h3 className="text-slate-500 text-sm font-medium mb-1">{title}</h3>
    <div className="flex items-end gap-2">
      <span className="text-2xl font-bold text-slate-900">{level}%</span>
      <span className="text-xs text-slate-400 mb-1">Stock Level</span>
    </div>
    <div className="mt-4 w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${level}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
        className={`h-full rounded-full ${level < 30 ? "bg-red-500" : level < 60 ? "bg-yellow-500" : "bg-blue-600"
          }`}
      />
    </div>
  </div>
);

const LivePulse = () => (
  <span className="relative flex h-2 w-2">
    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
    <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
  </span>
);

const HotspotAlert = () => (
  <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 w-72">
    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
      Hotspot Alerts
      <span className="px-1.5 py-0.5 bg-red-50 text-red-600 rounded text-[10px]">Live</span>
    </h3>
    <div className="space-y-4">
      {[
        { area: "Nagpur South", score: 12, time: "2 hours" },
        { area: "Wardha Center", score: 8, time: "1 hour" },
        { area: "Amravati North", score: 15, time: "30 mins" },
      ].map((alert, i) => (
        <div key={i} className="flex items-start gap-3">
          <div className="mt-1">
            {alert.score >= 10 ? <LivePulse /> : <div className="w-2 h-2 rounded-full bg-slate-300" />}
          </div>
          <div>
            <div className="text-sm font-bold text-slate-800">{alert.area}</div>
            <div className="text-[11px] text-slate-500">
              {alert.score} reports in {alert.time}
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const HotspotMap = () => (
  <div className="flex gap-6 h-[500px]">
    <div className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
        <h3 className="font-bold text-slate-800">AI Need Hotspots</h3>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs font-medium text-slate-600 italic">
            AI Clustering: High-density request zone detected
          </span>
        </div>
      </div>
      <div className="relative flex-1 bg-slate-200 overflow-hidden">
        {/* Map Placeholder Content */}
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#000_1px,transparent_1px)] [background-size:20px_20px]" />

        {/* Hotspot 1 */}
        <div className="absolute top-1/4 left-1/3">
          <motion.div
            animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0.2, 0.5] }}
            transition={{ repeat: Infinity, duration: 2 }}
            className="w-16 h-16 bg-red-500 rounded-full -ml-8 -mt-8"
          />
          <div className="w-4 h-4 bg-red-600 rounded-full border-2 border-white -ml-2 -mt-2 relative z-10" />
        </div>

        {/* Hotspot 2 */}
        <div className="absolute bottom-1/3 right-1/4">
          <motion.div
            animate={{ scale: [1, 1.8, 1], opacity: [0.4, 0.1, 0.4] }}
            transition={{ repeat: Infinity, duration: 2.5 }}
            className="w-24 h-24 bg-red-400 rounded-full -ml-12 -mt-12"
          />
          <div className="w-4 h-4 bg-red-500 rounded-full border-2 border-white -ml-2 -mt-2 relative z-10" />
        </div>

        {/* Legend Overlay */}
        <div className="absolute bottom-6 left-6 bg-white p-4 rounded-lg shadow-lg border border-slate-100">
          <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-2">Map Legend</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <LivePulse /> Critical Needs ({'>'} 50)
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <div className="w-2 h-2 rounded-full bg-yellow-500" /> Emerging Issues (10-50)
            </div>
          </div>
        </div>
      </div>
    </div>
    <HotspotAlert />
  </div>
);


const PriorityTable = ({ requests }) => (
  <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
    <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
      <h3 className="font-bold text-slate-800">Priority Requests</h3>
      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{requests.length} Active Reports</span>
    </div>
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr className="bg-slate-50 text-[10px] uppercase tracking-wider font-bold text-slate-400 border-b border-slate-100">
            <th className="px-6 py-4">Request Description</th>
            <th className="px-6 py-4">Location</th>
            <th className="px-6 py-4">Time Remaining</th>
            <th className="px-6 py-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {requests.map((req) => {
            const deadline = calculateDeadline(req.reportedAt, req.urgency);
            const { total, days, hours } = getTimeRemaining(deadline);
            const isCritical = req.urgency === URGENCY.CRITICAL;
            const hoursSinceReported = (new Date().getTime() - new Date(req.reportedAt).getTime()) / (1000 * 60 * 60);
            const shouldPulse = isCritical && hoursSinceReported > 12;

            // Simple progress calculation (max 7 days)
            const maxWindow = (req.urgency === URGENCY.CRITICAL ? 1 : req.urgency === URGENCY.HIGH ? 3 : 7) * 24 * 60 * 60 * 1000;
            const progress = Math.max(0, Math.min(100, (total / maxWindow) * 100));

            return (
              <motion.tr
                key={req.id}
                animate={shouldPulse ? {
                  backgroundColor: ["#ffffff", "#fef2f2", "#ffffff"],
                  boxShadow: ["none", "inset 0 0 10px rgba(239, 68, 68, 0.1)", "none"]
                } : {}}
                transition={shouldPulse ? { repeat: Infinity, duration: 2 } : {}}
                className="hover:bg-slate-50 transition-colors"
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {shouldPulse && <div className="w-2 h-2 rounded-full bg-red-500 animate-ping" />}
                    <div>
                      <div className="text-sm font-medium text-slate-900">{req.title}</div>
                      <div className="text-xs text-slate-400">{req.category}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-1.5 text-sm text-slate-600">
                    <svg className="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    {req.location.city}, {req.location.pincode}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="w-32">
                    <div className="flex justify-between text-[10px] font-bold mb-1">
                      <span className={total < 1000 * 60 * 60 * 12 ? "text-red-600" : "text-slate-500"}>
                        {days > 0 ? `${days}d ` : ""}{hours}h left
                      </span>
                      <span className="text-slate-400">{Math.round(progress)}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        className={`h-full rounded-full ${progress < 25 ? "bg-red-500" : progress < 50 ? "bg-yellow-500" : "bg-blue-600"}`}
                      />
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="px-3 py-1.5 bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white rounded-lg text-xs font-bold transition-all">
                    Respond
                  </button>
                </td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>
    </div>
  </div>
);

export default function NGODashboard() {
  const [activeTab, setActiveTab] = useState("inventory");
  const [showNearby, setShowNearby] = useState(false);

  // Simulated NGO context
  const ngoCity = "Nagpur";
  const ngoPincode = "440009"; // Matching one of the mock needs

  const filteredRequests = mockNeeds.filter(req => {
    // Primary Filter: Only show requests in NGO's registered city
    if (req.location.city !== ngoCity) return false;

    // Optional Filter: Show nearby (same pincode)
    if (showNearby) {
      return req.location.pincode === ngoPincode;
    }

    return true;
  });

  return (
    <div className="flex gap-8 py-8">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 flex flex-col gap-2">
        <SidebarItem
          label="Inventory"
          icon="📦"
          active={activeTab === "inventory"}
          onClick={() => setActiveTab("inventory")}
        />
        <SidebarItem
          label="Need Hotspots"
          icon="🎯"
          active={activeTab === "hotspots"}
          onClick={() => setActiveTab("hotspots")}
        />
        <SidebarItem
          label="Task Manager"
          icon="📋"
          active={activeTab === "tasks"}
          onClick={() => setActiveTab("tasks")}
        />
      </aside>

      {/* Main Content Area */}
      <main className="flex-1">
        <AnimatePresence mode="wait">
          {activeTab === "inventory" && (
            <motion.div
              key="inventory"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              {/* Operational Toggles */}
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div className="flex gap-4">
                  <button className="px-6 py-3 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-100 text-sm font-bold flex items-center gap-2">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    {ngoCity} Command
                  </button>
                  <button
                    onClick={() => setShowNearby(!showNearby)}
                    className={`px-6 py-3 border rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${showNearby
                        ? "bg-amber-50 border-amber-200 text-amber-700 shadow-sm"
                        : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                      }`}
                  >
                    <span>📍</span>
                    Nearby Requests {showNearby && `(${ngoPincode})`}
                  </button>
                </div>
                
                <div className="flex gap-2">
                  <button className="p-3 bg-white text-slate-600 border border-slate-200 rounded-xl text-sm font-bold hover:bg-slate-50 transition-colors">
                    My Active Tasks
                  </button>
                  <button className="p-3 bg-white text-slate-600 border border-slate-200 rounded-xl text-sm font-bold hover:bg-slate-50 transition-colors flex items-center gap-2">
                    <span className="text-red-500">⚠️</span>
                    Stock Alerts
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <InventoryCard title="Food Supply" level={82} icon="🥘" />
                <InventoryCard title="Medical Kits" level={24} icon="💊" />
                <InventoryCard title="Shelter Units" level={56} icon="🏠" />
                <InventoryCard title="Rescue Tools" level={91} icon="🛠️" />
              </div>
              <PriorityTable requests={filteredRequests} />
            </motion.div>
          )}


          {activeTab === "hotspots" && (
            <motion.div
              key="hotspots"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <HotspotMap />
            </motion.div>
          )}

          {activeTab === "tasks" && (
            <motion.div
              key="tasks"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center">
                <div className="text-4xl mb-4">👷</div>
                <h3 className="text-lg font-bold text-slate-800">Task Manager Module</h3>
                <p className="text-slate-500 mt-2">Integrating with Volunteer Matching system...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}


