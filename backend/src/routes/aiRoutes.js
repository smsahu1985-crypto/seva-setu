const express = require("express");
const router = express.Router();
const aiController = require("../controllers/aiController");

router.post("/priority", aiController.getPriority);
router.get("/priority/health", aiController.getPriorityHealth);

router.post("/recommend", aiController.getRecommendations);
router.post("/recommend/batch", aiController.getBatchRecommendations);
router.get("/recommend/health", aiController.getRecommendHealth);

router.post("/autofill", aiController.getAutofill);
router.post("/fraud", aiController.getFraudScore);

router.get("/health", aiController.getAllHealth);

module.exports = router;
