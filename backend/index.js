require("dotenv").config();

const express = require("express");
const cors = require("cors");
const path = require("path");
const app = express();

const requestRoutes = require("./src/routes/requestRoutes");
const taskRoutes = require("./src/routes/taskRoutes");
const volunteerRoutes = require("./src/routes/volunteerRoutes");
const assignmentRoutes = require("./src/routes/assignmentRoutes");
const inventoryRoutes = require("./src/routes/inventoryRoutes");
const aiRoutes = require("./src/routes/aiRoutes");
const recommendRoutes = require("./src/routes/recommendRoutes");

app.use(cors({
  origin: process.env.CORS_ORIGIN || true,
  credentials: true,
}));
app.use(express.json({ limit: "1mb" }));
app.use("/api", requestRoutes);
app.use("/api", taskRoutes);
app.use("/api", volunteerRoutes);
app.use("/api", assignmentRoutes);
app.use("/api", inventoryRoutes);
app.use("/api/ai", aiRoutes);
app.use("/api", recommendRoutes);

app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    service: "SevaSetu Backend",
    ai: {
      priority: process.env.PRIORITY_AI_URL || "http://localhost:8000",
      recommendations: process.env.RECOMMEND_AI_URL || "http://localhost:8001",
      autofill: process.env.AUTOFILL_AI_URL || "http://localhost:8002",
      fraud: process.env.FRAUD_AI_URL || "http://localhost:8003",
    },
  });
});

app.get("/api", (req, res) => {
  res.send("Backend running");
});

const frontendDist = path.join(__dirname, "..", "frontend", "dist");
app.use(express.static(frontendDist));
app.get(/.*/, (req, res, next) => {
  if (req.path.startsWith("/api")) return next();
  res.sendFile(path.join(frontendDist, "index.html"), (err) => {
    if (err) next();
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});


