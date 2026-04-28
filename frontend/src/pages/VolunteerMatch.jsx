import React, { useState, useEffect } from "react";
import { mockNeeds, STATUS } from "../data/mockNeeds";

const TaskCard = ({ need }) => {
  const [status, setStatus] = useState("idle"); // idle | loading | applied

  const handleApply = () => {
    setStatus("loading");
    setTimeout(() => {
      setStatus("applied");
    }, 1000);
  };

  const isMumbaiMatch = need.location.city.toLowerCase() === "mumbai";

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row items-start md:items-center gap-6 hover:border-blue-300 transition-colors duration-200">
      {/* Content */}
      <div className="flex-1">
        <div className="flex flex-wrap items-center gap-3 mb-2">
          <h3 className="text-xl font-bold text-gray-900">{need.title}</h3>
          {isMumbaiMatch && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800 border border-green-200">
              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
              </svg>
              Matching your location
            </span>
          )}
        </div>
        
        <p className="text-sm text-blue-600 font-medium mb-3">
          Organized by: {need.reportedBy}
        </p>
        
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            </svg>
            {need.location.city}, {need.location.state}
          </div>
          <div className="flex items-center font-medium">
            <svg className="w-4 h-4 mr-1.5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3.005 3.005 0 013.75-2.906z" />
            </svg>
            {need.volunteersAssigned} of {need.volunteersNeeded} volunteers assigned
          </div>
        </div>
      </div>

      {/* Action Area */}
      <div className="w-full md:w-auto flex-shrink-0">
        <button
          onClick={handleApply}
          disabled={status !== "idle"}
          className={`w-full md:w-48 flex items-center justify-center px-6 py-3 rounded-lg font-bold text-sm transition-all duration-200 ${
            status === "idle"
              ? "bg-blue-700 text-white hover:bg-blue-800 shadow-sm hover:shadow"
              : status === "loading"
              ? "bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
              : "bg-green-100 text-green-700 border border-green-200 cursor-default"
          }`}
        >
          {status === "idle" && "Apply for Mission"}
          {status === "loading" && (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading...
            </>
          )}
          {status === "success" && (
            <>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              Application Sent
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default function VolunteerMatch() {
  const [applications, setApplications] = useState({});

  const handleApply = (id) => {
    setApplications((prev) => ({ ...prev, [id]: "loading" }));
    setTimeout(() => {
      setApplications((prev) => ({ ...prev, [id]: "success" }));
    }, 1000);
  };

  const missions = mockNeeds.filter(
    (need) => need.status === STATUS.OPEN || need.status === STATUS.IN_PROGRESS
  );

  return (
    <div className="py-8 space-y-10">
      <header>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Available Missions for You</h1>
        <p className="text-gray-500">Find a cause that matches your expertise and location.</p>
      </header>

      {/* Search & Filter Bar */}
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="flex-1 relative group">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            className="w-full pl-12 pr-4 py-4 bg-white rounded-2xl shadow-md focus:shadow-lg focus:outline-none border-none transition-all placeholder-slate-400 text-slate-700"
            placeholder="Search missions by city, skill, or NGO..."
          />
        </div>
        <div className="flex flex-wrap gap-3">
          <select className="px-4 py-4 bg-white rounded-2xl shadow-md border-none focus:outline-none text-slate-600 text-sm font-medium cursor-pointer min-w-[140px]">
            <option>Distance: All</option>
            <option>Within 5km</option>
            <option>Within 10km</option>
          </select>
          <select className="px-4 py-4 bg-white rounded-2xl shadow-md border-none focus:outline-none text-slate-600 text-sm font-medium cursor-pointer min-w-[140px]">
            <option>Skill: Medical</option>
            <option>Skill: Logistics</option>
            <option>Skill: Teaching</option>
          </select>
          <select className="px-4 py-4 bg-white rounded-2xl shadow-md border-none focus:outline-none text-slate-600 text-sm font-medium cursor-pointer min-w-[140px]">
            <option>Urgency: All</option>
            <option>High Priority</option>
            <option>Critical Only</option>
          </select>
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-6">
        {missions.length > 0 ? (
          missions.map((mission) => (
            <TaskCard
              key={mission.id}
              need={mission}
              status={applications[mission.id]}
              onApply={() => handleApply(mission.id)}
            />
          ))
        ) : (
          <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300">
            <p className="text-gray-500">No active missions found at the moment.</p>
          </div>
        )}
      </div>
    </div>
  );
}
