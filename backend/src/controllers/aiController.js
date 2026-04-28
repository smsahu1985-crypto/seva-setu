const axios = require("axios");

const PRIORITY_AI_URL = process.env.PRIORITY_AI_URL || "http://localhost:8000";
const RECOMMEND_AI_URL = process.env.RECOMMEND_AI_URL || "http://localhost:8001";
const AUTOFILL_AI_URL = process.env.AUTOFILL_AI_URL || "http://localhost:8002";
const FRAUD_AI_URL = process.env.FRAUD_AI_URL || "http://localhost:8003";
const AI_TIMEOUT_MS = Number(process.env.AI_TIMEOUT_MS || 8000);

const post = (baseUrl, endpoint, body) =>
  axios.post(`${baseUrl}${endpoint}`, body, { timeout: AI_TIMEOUT_MS });

const get = (baseUrl, endpoint) =>
  axios.get(`${baseUrl}${endpoint}`, { timeout: 3000 });

exports.getPriority = async (req, res) => {
  try {
    const response = await post(PRIORITY_AI_URL, "/predict-priority", req.body);
    res.json(response.data);
  } catch (error) {
    console.error("Priority AI Error:", error.message);
    res.status(error.response?.status || 500).json({
      error: "Failed to get priority prediction",
      details: error.response?.data?.detail || error.message,
    });
  }
};

exports.getPriorityHealth = async (req, res) => {
  try {
    const response = await get(PRIORITY_AI_URL, "/health");
    res.json(response.data);
  } catch (error) {
    res.status(503).json({
      error: "Priority AI service unavailable",
      details: error.message,
    });
  }
};

exports.getRecommendations = async (req, res) => {
  try {
    const {
      volunteer_profile,
      tasks,
      top_k,
      apply_diversity,
      filter_full_tasks,
      radius_km,
    } = req.body;

    const response = await post(RECOMMEND_AI_URL, "/recommend-tasks", {
      volunteer_profile,
      tasks,
      top_k: top_k || 5,
      apply_diversity: apply_diversity !== false,
      filter_full_tasks: filter_full_tasks || false,
      radius_km,
    });

    res.json(response.data);
  } catch (error) {
    console.error("Recommend AI Error:", error.message);
    res.status(error.response?.status || 500).json({
      error: "Failed to get recommendations",
      details: error.response?.data?.detail || error.message,
    });
  }
};

exports.getBatchRecommendations = async (req, res) => {
  try {
    const response = await post(RECOMMEND_AI_URL, "/recommend-batch", req.body);
    res.json(response.data);
  } catch (error) {
    console.error("Recommend AI Batch Error:", error.message);
    res.status(error.response?.status || 500).json({
      error: "Failed to get batch recommendations",
      details: error.response?.data?.detail || error.message,
    });
  }
};

exports.getRecommendHealth = async (req, res) => {
  try {
    const response = await get(RECOMMEND_AI_URL, "/health");
    res.json(response.data);
  } catch (error) {
    res.status(503).json({
      error: "Recommendation AI service unavailable",
      details: error.message,
    });
  }
};

exports.getAutofill = async (req, res) => {
  try {
    const request_description =
      req.body.request_description || req.body.description || "";
    const response = await post(AUTOFILL_AI_URL, "/autofill", {
      request_description,
    });
    res.json(response.data);
  } catch (error) {
    console.error("Autofill AI Error:", error.message);
    res.status(error.response?.status || 500).json({
      error: "Failed to autofill request",
      details: error.response?.data?.detail || error.message,
    });
  }
};

exports.getFraudScore = async (req, res) => {
  try {
    const response = await post(FRAUD_AI_URL, "/detect-fraud", req.body);
    res.json(response.data);
  } catch (error) {
    console.error("Fraud AI Error:", error.message);
    res.status(error.response?.status || 500).json({
      error: "Failed to score fraud risk",
      details: error.response?.data?.detail || error.message,
    });
  }
};

exports.getAllHealth = async (req, res) => {
  const health = {
    priority_ai: { status: "unknown" },
    recommend_ai: { status: "unknown" },
    autofill_ai: { status: "unknown" },
    fraud_ai: { status: "unknown" },
  };

  for (const [key, url] of [
    ["priority_ai", PRIORITY_AI_URL],
    ["recommend_ai", RECOMMEND_AI_URL],
    ["autofill_ai", AUTOFILL_AI_URL],
    ["fraud_ai", FRAUD_AI_URL],
  ]) {
    try {
      const response = await get(url, "/health");
      health[key] = { status: "healthy", ...response.data };
    } catch (error) {
      health[key] = { status: "unavailable", error: error.message };
    }
  }

  const allHealthy = Object.values(health).every((item) => item.status === "healthy");
  res.status(allHealthy ? 200 : 503).json(health);
};
