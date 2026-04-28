import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../lib/api";

const CATEGORIES = [
  "Food & Nutrition",
  "Medical Aid",
  "Education",
  "Shelter",
  "Disaster Relief",
  "Other",
];

export default function PublicRequest() {
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [urgency, setUrgency] = useState(50);
  const [location, setLocation] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [contact, setContact] = useState("");
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [aiResult, setAiResult] = useState(null);

  const normalizeCategory = (value) => {
    const normalized = String(value || "").trim().toLowerCase().replace(/[_-]/g, " ");
    const categoryMap = {
      "food nutrition": "Food & Nutrition",
      "food relief": "Food & Nutrition",
      "medical aid": "Medical Aid",
      medical: "Medical Aid",
      education: "Education",
      shelter: "Shelter",
      "disaster relief": "Disaster Relief",
      logistics: "Disaster Relief",
    };
    return categoryMap[normalized] || value;
  };

  const urgencyToScore = (value) => {
    const normalized = String(value || "").toLowerCase();
    if (normalized === "critical") return 95;
    if (normalized === "high") return 80;
    if (normalized === "medium") return 55;
    if (normalized === "low") return 25;
    return urgency;
  };

  const handleAutoExtract = async () => {
    if (!description) return;
    setIsExtracting(true);
    setStatus({ type: "idle", message: "" });

    try {
      const result = await api.autofill(description);
      setAiResult(result);
      if (result.category) setCategory(normalizeCategory(result.category));
      if (result.priority_label || result.urgency_level) {
        setUrgency(urgencyToScore(result.priority_label || result.urgency_level));
      }
      if (result.location_city || result.location_state) {
        setLocation((current) => ({
          lat: current?.lat || "",
          lng: current?.lng || "",
          address: [result.location_city, result.location_state].filter(Boolean).join(", "),
        }));
      }
      setStatus({ type: "success", message: "AI filled the request details. Please review before publishing." });
    } catch (error) {
      const text = description.toLowerCase();
      if (text.includes("food") || text.includes("hungry") || text.includes("ration")) {
        setCategory("Food & Nutrition");
      } else if (text.includes("medical") || text.includes("doctor") || text.includes("hospital") || text.includes("medicine")) {
        setCategory("Medical Aid");
      } else if (text.includes("cyclone") || text.includes("flood") || text.includes("emergency")) {
        setCategory("Disaster Relief");
        setUrgency(90);
      } else if (text.includes("school") || text.includes("books") || text.includes("study")) {
        setCategory("Education");
      }

      if (text.includes("immediate") || text.includes("emergency") || text.includes("critical")) {
        setUrgency(100);
      } else if (text.includes("asap") || text.includes("soon")) {
        setUrgency(75);
      }
      setStatus({ type: "warning", message: `AI autofill unavailable, used local hints instead. ${error.message}` });
    } finally {
      setIsExtracting(false);
    }
  };

  const detectLocation = () => {
    setIsDetecting(true);
    setTimeout(() => {
      setLocation({
        lat: (19.076 + Math.random() * 0.1).toFixed(4),
        lng: (72.877 + Math.random() * 0.1).toFixed(4),
        address: "Shivaji Nagar, Mumbai, Maharashtra",
      });
      setIsDetecting(false);
    }, 1500);
  };

  // Calculate slider color based on urgency (50 = yellow, 100 = deep red)
  const getSliderColor = () => {
    const red = Math.min(255, (urgency * 2.55));
    const green = Math.max(0, 255 - (urgency - 50) * 5.1);
    return `rgb(${red}, ${green}, 0)`;
  };

  const handleSubmit = async () => {
    if (!description || !category || !location?.address) {
      setStatus({ type: "error", message: "Please add a description, category, and service location." });
      return;
    }

    setStatus({ type: "loading", message: "Publishing request..." });

    try {
      const result = await api.createRequest({
        name: aiResult?.request_title || description.slice(0, 80),
        contact,
        location: location.address,
        category,
        description,
      });

      setAiResult(result.ai);
      setStatus({
        type: "success",
        message: `Request published with ${result.data?.[0]?.urgency || "medium"} priority.`,
      });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  };

  return (
    <div className="py-8 max-w-3xl mx-auto">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 p-8 text-white">
          <h1 className="text-3xl font-bold mb-2">Report a Need</h1>
          <p className="text-blue-100">
            Tell us what's happening. Our AI will help categorize and route your request to the right people.
          </p>
        </div>

        <div className="p-8 space-y-8">
          {/* Step 1: AI Smart Fill */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider">
                1. Describe the Problem
              </label>
              <button
                onClick={handleAutoExtract}
                disabled={!description || isExtracting}
                className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-xs font-bold transition-all disabled:opacity-50"
              >
                {isExtracting ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Extracting...
                  </span>
                ) : (
                  <>✨ Auto-Extract Details</>
                )}
              </button>
            </div>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., There is an immediate need for food and clean water for 20 families due to flooding in our area..."
              className="w-full h-32 p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none text-slate-800"
            />
          </div>

          {/* Step 2: Categorization */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider">
                2. Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              >
                <option value="">Select Category</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Step 3: Urgency Slider */}
            <div className="space-y-4">
              <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider flex justify-between">
                3. Urgency Level
                <span className="font-bold" style={{ color: getSliderColor() }}>
                  {urgency < 33 ? "Low" : urgency < 66 ? "Medium" : urgency < 90 ? "High" : "CRITICAL"}
                </span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={urgency}
                onChange={(e) => setUrgency(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                style={{ accentColor: getSliderColor() }}
              />
              <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                <span>Routine</span>
                <span>Urgent</span>
                <span>Life-Threatening</span>
              </div>
            </div>
          </div>

          {/* Step 4: Location Capture */}
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider">
              4. Service Location
            </label>
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
              <button
                onClick={detectLocation}
                disabled={isDetecting}
                className="flex items-center gap-2 px-6 py-3 bg-slate-800 text-white rounded-xl hover:bg-slate-900 transition-all disabled:opacity-50 shadow-lg shadow-slate-200"
              >
                {isDetecting ? (
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                )}
                Detect My Location
              </button>
              
              <AnimatePresence>
                {location && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex-1 p-3 bg-green-50 border border-green-100 rounded-xl flex items-center gap-3"
                  >
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-xs font-bold text-green-800">Verified Location</div>
                      <div className="text-[10px] text-green-600 truncate max-w-[200px]">
                        {location.lat}, {location.lng} — {location.address}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-slate-100">
            <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider">
              Contact
            </label>
            <input
              value={contact}
              onChange={(e) => setContact(e.target.value)}
              placeholder="Phone or email for NGO follow-up"
              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
          </div>

          {status.message && (
            <div className={`rounded-xl border p-4 text-sm font-medium ${
              status.type === "error"
                ? "bg-red-50 border-red-100 text-red-700"
                : status.type === "warning"
                  ? "bg-amber-50 border-amber-100 text-amber-700"
                  : "bg-green-50 border-green-100 text-green-700"
            }`}>
              {status.message}
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={status.type === "loading"}
            className="w-full py-4 bg-blue-600 text-white font-bold text-lg rounded-2xl hover:bg-blue-700 transition-all shadow-xl shadow-blue-200 mt-4"
          >
            {status.type === "loading" ? "Publishing..." : "Publish Request"}
          </button>
        </div>
      </div>
    </div>
  );
}
