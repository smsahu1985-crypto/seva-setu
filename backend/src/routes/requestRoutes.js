const express = require("express");
const router = express.Router();
const supabase = require("../config/supabaseClient");

router.get("/get-requests", async (req, res) => {
  const { data, error } = await supabase
    .from("requests")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) return res.status(500).json({ error: error.message });

  res.json({ data });
});

router.post("/create-request", async (req, res) => {
  const {
    name,
    contact,
    location,
    category,
    description,
    urgency
  } = req.body;

  const { data, error } = await supabase
    .from("requests")
    .insert([{
      name,
      contact,
      location,
      category,
      description,
      urgency
    }])
    .select();

  if (error) return res.status(500).json({ error: error.message });

  res.json({ data });
});

module.exports = router;