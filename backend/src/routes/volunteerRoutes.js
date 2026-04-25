const express = require("express");
const router = express.Router();
const supabase = require("../config/supabaseClient");

router.post("/create-volunteer", async (req, res) => {
  const { name, contact, location, skills, availability } = req.body;

  if (!name || !location) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  const { data, error } = await supabase
    .from("volunteers")
    .insert([{ name, contact, location, skills, availability }])
    .select();

  if (error) return res.status(500).json({ error: error.message });

  res.json({ data });
});

module.exports = router;