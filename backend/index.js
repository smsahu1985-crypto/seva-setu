require("dotenv").config();

const express = require("express");
const app = express();

const requestRoutes = require("./src/routes/requestRoutes");
const taskRoutes = require("./src/routes/taskRoutes");
const volunteerRoutes = require("./src/routes/volunteerRoutes");
const assignmentRoutes = require("./src/routes/assignmentRoutes");
const inventoryRoutes = require("./src/routes/inventoryRoutes");

app.use(express.json());
app.use("/api", requestRoutes);
app.use("/api", taskRoutes);
app.use("/api", volunteerRoutes);
app.use("/api", assignmentRoutes);
app.use("/api", inventoryRoutes);

app.get("/", (req, res) => {
  res.send("Backend running");
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});


