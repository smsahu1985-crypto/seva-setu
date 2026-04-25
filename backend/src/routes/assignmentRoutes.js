const express = require("express");
const router = express.Router();
const supabase = require("../config/supabaseClient");

// CREATE ASSIGNMENT
router.post("/create-assignment", async (req, res) => {
  const { task_id, volunteer_id, status, proof_image } = req.body;
  const { data, error } = await supabase
    .from("task_assignments")
    .insert([{ task_id, volunteer_id, status, proof_image }])
    .select();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

// GET ALL ASSIGNMENTS
router.get("/assignments", async (req, res) => {
  const { data, error } = await supabase
    .from("task_assignments")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

// UPDATE ASSIGNMENT
router.put("/assignment/:id", async (req, res) => {
  const id = parseInt(req.params.id);
  const { status, proof_image } = req.body;
  const { data, error } = await supabase
    .from("task_assignments")
    .update({ status, proof_image })
    .eq("id", id)
    .select();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

// DELETE ASSIGNMENT
router.delete("/assignment/:id", async (req, res) => {
  const { id } = req.params;
  const { data, error } = await supabase
    .from("task_assignments")
    .delete()
    .eq("id", id)
    .select();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

module.exports = router;
