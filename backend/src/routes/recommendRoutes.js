const express = require("express");
const router = express.Router();
const supabase = require("../config/supabaseClient");
const axios = require("axios");

const RECOMMEND_AI_URL =
  process.env.RECOMMEND_AI_URL || "http://localhost:8001";

// ===============================
// BUILD TASK FOR AI (FULL SAFE)
// ===============================
function buildTaskForAI(request) {
  return {
    task_id: request.id || 1,
    task_title: request.name || "General Task",
    task_category: request.category || "general",
    ngo_name: "SevaSetu",

    task_description: request.description || "",

    latitude: 19.076,
    longitude: 72.8777,

    required_skills: [request.category || "general"],

    task_priority_score:
      request.urgency === "critical"
        ? 90
        : request.urgency === "high"
          ? 70
          : request.urgency === "medium"
            ? 45
            : 20,

    deadline_hours_remaining: 48,

    requires_vehicle:
      request.description?.toLowerCase().includes("transport") ||
      request.description?.toLowerCase().includes("deliver") ||
      request.description?.toLowerCase().includes("drive") ||
      false,

    required_volunteers_count: 5,
    currently_assigned_count: 0,
  };
}

// ===============================
// BUILD VOLUNTEER FOR AI (FULL SAFE)
// ===============================
function buildVolunteerForAI(volunteer) {
  return {
    volunteer_id: volunteer.id,

    skills: volunteer.skills
      ? volunteer.skills.split(",").map((s) => s.trim().toLowerCase())
      : ["general"],

    latitude: 19.076,
    longitude: 72.8777,

    max_travel_km: 25,
    vehicle_type: "bike",

    availability: volunteer.availability || "weekends",

    volunteer_level: "regular",
    reliability_score: 80,
  };
}

// ===============================
// ROUTE
// ===============================
router.post("/recommend-volunteers/:requestId", async (req, res) => {
  const { requestId } = req.params;

  try {
    // 1. GET REQUEST
    const { data: request, error: requestError } = await supabase
      .from("requests")
      .select("*")
      .eq("id", requestId)
      .single();

    if (requestError) {
      return res.status(404).json({ error: "Request not found" });
    }

    // 2. GET VOLUNTEERS (NO FILTER)
    const { data: volunteers, error: volunteerError } = await supabase
      .from("volunteers")
      .select("*");

    console.log("VOLUNTEERS:", volunteers);

    if (volunteerError) {
      return res.status(500).json({ error: "Failed to fetch volunteers" });
    }

    if (!volunteers || volunteers.length === 0) {
      return res.json({
        request_id: requestId,
        recommendations: [],
        total_volunteers_evaluated: 0,
      });
    }

    // 3. BUILD TASK
    const taskForAI = buildTaskForAI(request);

    const results = [];

    // 4. LOOP VOLUNTEERS
    for (const vol of volunteers) {
      try {
        const volunteerProfile = buildVolunteerForAI(vol);

        const aiRes = await axios.post(`${RECOMMEND_AI_URL}/recommend-tasks`, {
          tasks: [taskForAI],
          volunteer_profile: volunteerProfile,
        });

        const rec = aiRes.data.recommendations?.[0];

        if (rec) {
          results.push({
            volunteer_id: vol.id,
            name: vol.name,
            match_score: rec.score || rec.match_score || 0,
            reasoning: rec.reasoning || "",
          });
        }
      } catch (err) {
        console.error("AI ERROR:", err.response?.data || err.message);
      }
    }

    // 5. SORT
    results.sort((a, b) => b.match_score - a.match_score);

    // 6. RETURN
    res.json({
      request_id: requestId,
      total_volunteers_evaluated: results.length,
      recommendations: results.slice(0, 5),
    });
  } catch (err) {
    console.error("FINAL ERROR:", err.message);
    res.status(500).json({ error: "Something broke" });
  }
});

module.exports = router;
