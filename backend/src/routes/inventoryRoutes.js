const express = require("express");
const router = express.Router();
const supabase = require("../config/supabaseClient");

// CREATE INVENTORY ITEM
router.post("/create-inventory", async (req, res) => {
  const { ngo_id, item_name, quantity } = req.body;
  const { data, error } = await supabase
    .from("inventory")
    .insert([{ ngo_id, item_name, quantity }])
    .select();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

// GET ALL INVENTORY ITEMS
router.get("/inventory", async (req, res) => {
  const { data, error } = await supabase
    .from("inventory")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

// UPDATE INVENTORY ITEM
router.put("/inventory/:id", async (req, res) => {
  const { id } = req.params;
  const { ngo_id, item_name, quantity } = req.body;
  const { data, error } = await supabase
    .from("inventory")
    .update({ ngo_id, item_name, quantity })
    .eq("id", id)
    .select();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

// DELETE INVENTORY ITEM
router.delete("/inventory/:id", async (req, res) => {
  const { id } = req.params;
  const { data, error } = await supabase
    .from("inventory")
    .delete()
    .eq("id", id)
    .select();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ data });
});

module.exports = router;
