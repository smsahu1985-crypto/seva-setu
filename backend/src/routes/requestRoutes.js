const express = require("express");
const router = express.Router();
const supabase = require("../config/supabaseClient");
const axios = require("axios");

const PRIORITY_AI_URL = process.env.PRIORITY_AI_URL || "http://localhost:8000";
const AUTOFILL_AI_URL = process.env.AUTOFILL_AI_URL || "http://localhost:8002";
const FRAUD_AI_URL = process.env.FRAUD_AI_URL || "http://localhost:8003";
const AI_TIMEOUT_MS = Number(process.env.AI_TIMEOUT_MS || 8000);

function normalizeUrgency(value) {
  const urgency = String(value || "medium").toLowerCase();
  if (["critical", "high", "medium", "low"].includes(urgency)) return urgency;
  return "medium";
}

function normalizeCategory(value) {
  const normalized = String(value || "Other").trim().toLowerCase().replace(/[_-]/g, " ");
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
  return categoryMap[normalized] || value || "Other";
}

function buildPriorityPayload(fields) {
  return {
    task_title: fields.title || fields.name || "Community help request",
    task_description: fields.description || "",
    task_category: fields.category || "Other",
    location: fields.location || fields.location_city || "Unknown",
    disaster_type: fields.is_disaster_related ? "Disaster" : "None",
    requested_volunteers_count: fields.volunteers_needed || 3,
    deadline_hours: fields.deadline_hours || 72,
    created_hour: new Date().getHours(),
    ngo_manual_urgency: fields.urgency || fields.urgency_level || "medium",
  };
}

function buildFraudPayload(fields) {
  const locationParts = String(fields.location || "").split(",").map((part) => part.trim());
  return {
    request_title: fields.title || fields.name || "Community help request",
    request_description: fields.description || "",
    category: fields.category || "unknown",
    location_city: fields.location_city || locationParts[0] || "",
    location_state: fields.location_state || locationParts[1] || "",
    people_affected: fields.estimated_people_affected || 1,
    volunteers_needed: fields.volunteers_needed || 0,
    required_items: fields.required_items || [],
    deadline_hours: fields.deadline_hours || 24,
    contact_phone: fields.contact || "",
    user_type: "public",
    created_at_hour: new Date().getHours(),
  };
}

async function tryAutofill(description) {
  if (!description || description.length < 10) return null;
  try {
    const response = await axios.post(
      `${AUTOFILL_AI_URL}/autofill`,
      { request_description: description },
      { timeout: AI_TIMEOUT_MS }
    );
    return response.data;
  } catch (err) {
    console.warn("Autofill AI failed, continuing without it:", err.message);
    return null;
  }
}

async function tryPriority(fields) {
  try {
    const response = await axios.post(
      `${PRIORITY_AI_URL}/predict-priority`,
      buildPriorityPayload(fields),
      { timeout: AI_TIMEOUT_MS }
    );
    return response.data;
  } catch (err) {
    console.warn("Priority AI failed, using fallback:", err.message);
    return null;
  }
}

async function tryFraud(fields) {
  try {
    const response = await axios.post(
      `${FRAUD_AI_URL}/detect-fraud`,
      buildFraudPayload(fields),
      { timeout: AI_TIMEOUT_MS }
    );
    return response.data;
  } catch (err) {
    console.warn("Fraud AI failed, continuing without it:", err.message);
    return null;
  }
}

router.get("/get-requests", async (req, res) => {
  const { data, error } = await supabase
    .from("requests")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) return res.status(500).json({ error: error.message });

  res.json({ data });
});

router.post("/create-request", async (req, res) => {
  const { name, contact, location, category, description } = req.body;

  if (!description || !location) {
    return res.status(400).json({ error: "description and location are required" });
  }

  const autofill = await tryAutofill(description);
  const mergedFields = {
    ...autofill,
    name: name || autofill?.request_title || "Anonymous request",
    contact,
    location: location || [autofill?.location_city, autofill?.location_state].filter(Boolean).join(", "),
    category: normalizeCategory(category || autofill?.category),
    description,
  };

  const [priority, fraud] = await Promise.all([
    tryPriority(mergedFields),
    tryFraud(mergedFields),
  ]);

  const finalUrgency = normalizeUrgency(
    priority?.priority || priority?.label || autofill?.priority_label || autofill?.urgency_level
  );

  const { data, error } = await supabase
    .from("requests")
    .insert([{
      name: mergedFields.name,
      contact,
      location: mergedFields.location,
      category: mergedFields.category,
      description,
      urgency: finalUrgency,
    }])
    .select();

  if (error) return res.status(500).json({ error: error.message });

  res.json({
    data,
    ai: {
      autofill,
      priority,
      fraud,
    },
  });
});

module.exports = router;
