const API_BASE_URL = import.meta.env.VITE_API_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.error || payload.details || "Request failed");
  }

  return payload;
}

export const api = {
  health: () => request("/api/health"),
  aiHealth: () => request("/api/ai/health"),
  autofill: (description) =>
    request("/api/ai/autofill", {
      method: "POST",
      body: JSON.stringify({ request_description: description }),
    }),
  createRequest: (payload) =>
    request("/api/create-request", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getRequests: () => request("/api/get-requests"),
  getTasks: () => request("/api/tasks"),
  recommendTasks: (payload) =>
    request("/api/ai/recommend", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
