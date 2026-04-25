const express = require("express");
const router = express.Router();
const supabase = require("../config/supabaseClient");

// CREATE TASK (also updates request status to "accepted")
router.post("/create-task", async (req, res) => {
  const {
    ngo_id,
    request_id,
    title,
    description,
    required_volunteers,
    deadline,
    urgency
  } = req.body;

  // Create the task
  const { data: taskData, error: taskError } = await supabase
    .from("tasks")
    .insert([{
      ngo_id,
      request_id,
      title,
      description,
      required_volunteers,
      deadline,
      urgency
    }])
    .select();

  if (taskError) return res.status(500).json({ error: taskError.message });

  // If request_id provided, update request status to "accepted"
  if (request_id) {
    await supabase
      .from("requests")
      .update({ status: "accepted" })
      .eq("id", request_id);
  }

  res.json({ data: taskData });
});

// GET ALL TASKS (with filters: status, urgency, location)
router.get("/tasks", async (req, res) => {
  const { status, urgency, location } = req.query;

  let query = supabase
    .from("tasks")
    .select(`
      *,
      requests (name, location, urgency)
    `)
    .order("created_at", { ascending: false });

  if (status) query = query.eq("status", status);
  if (urgency) query = query.eq("urgency", urgency);

  const { data, error } = await query;

  if (error) return res.status(500).json({ error: error.message });

  // Filter by location manually (since it's in related requests table)
  let filteredData = data;
  if (location) {
    filteredData = data.filter(task => 
      task.requests?.location?.toLowerCase().includes(location.toLowerCase())
    );
  }

  res.json({ data: filteredData });
});

// UPDATE TASK STATUS
router.put("/task/:id", async (req, res) => {
  const { id } = req.params;
  const { status, title, description, required_volunteers, deadline } = req.body;

  const { data, error } = await supabase
    .from("tasks")
    .update({ status, title, description, required_volunteers, deadline })
    .eq("id", id)
    .select();

  if (error) return res.status(500).json({ error: error.message });

  res.json({ data });
});

// ASSIGN TASK
router.post("/assign-task", async (req, res) => {
  const { task_id, volunteer_id } = req.body;

  const { data, error } = await supabase
    .from("task_assignments")
    .insert([{
      task_id,
      volunteer_id,
      status: "assigned"
    }])
    .select();

  if (error) return res.status(500).json({ error: error.message });

  res.json({ data });
});

// UPDATE ASSIGNMENT STATUS + PROOF IMAGE
router.put("/assignment/:id", async (req, res) => {
  const id = parseInt(req.params.id);
  const { status, proof_image } = req.body;

  const { data: assignmentData, error: assignmentError } = await supabase
    .from("task_assignments")
    .update({ status, proof_image })
    .eq("id", id)
    .select();

    

  if (assignmentError) return res.status(500).json({ error: assignmentError.message });

  // If task completed, reduce inventory (basic logic)
  if (status === "completed") {
    // Get task_id from assignment to find related inventory
    const { data: assignment } = await supabase
      .from("task_assignments")
      .select("task_id")
      .eq("id", id)
      .single();

    if (assignment?.task_id) {
      // Get task details
      const { data: task } = await supabase
        .from("tasks")
        .select("title")
        .eq("id", assignment.task_id)
        .single();

      // Try to reduce inventory item matching task title
      if (task?.title) {
        await supabase
          .from("inventory")
          .update({ quantity: supabase.raw("GREATEST(quantity - 1, 0)") })
          .like("item_name", `%${task.title}%`);
      }
    }
  }

  res.json({ data: assignmentData });
});

// RECOMMENDED TASKS (Basic Matching - AI MVP)
router.get("/recommended-tasks", async (req, res) => {
  const { location } = req.query;

  // Get all open tasks
  let query = supabase
    .from("tasks")
    .select(`
      *,
      requests (name, location, urgency)
    `)
    .eq("status", "open")
    .order("created_at", { ascending: false });

  const { data, error } = await query;

  if (error) return res.status(500).json({ error: error.message });

  // Filter by location if provided
  let filteredData = data;
  if (location) {
    filteredData = data.filter(task => 
      task.requests?.location?.toLowerCase().includes(location.toLowerCase())
    );
  }

  // Sort by urgency priority (high > medium > low)
  const urgencyOrder = { high: 1, medium: 2, low: 3 };
  filteredData.sort((a, b) => {
    const urgencyA = a.requests?.urgency?.toLowerCase() || "low";
    const urgencyB = b.requests?.urgency?.toLowerCase() || "low";
    return (urgencyOrder[urgencyA] || 3) - (urgencyOrder[urgencyB] || 3);
  });

  res.json({ data: filteredData });
});

module.exports = router;