import React, { useState } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import VolunteerMatch from "./pages/VolunteerMatch";
import NGODashboard from "./pages/NGODashboard";
import VolunteerPortal from "./pages/VolunteerPortal";
import PublicRequest from "./pages/PublicRequest";
import { motion, AnimatePresence } from "framer-motion";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
      
      <main className="pt-20 pb-24">
        <div className="max-w-7xl mx-auto px-4">
          <AnimatePresence mode="wait">
            {currentPage === "dashboard" && (
              <motion.div key="dashboard" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <Dashboard onNavigate={setCurrentPage} />
              </motion.div>
            )}
            
            {currentPage === "volunteer" && (
              <motion.div key="volunteer" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <VolunteerPortal />
              </motion.div>
            )}

            {currentPage === "ngo" && (
              <motion.div key="ngo" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <NGODashboard />
              </motion.div>
            )}

            {currentPage === "report" && (
              <motion.div key="report" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <PublicRequest />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}





export default App;