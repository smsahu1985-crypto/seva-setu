/**
 * mockNeeds.js
 * Simulated community need reports for Seva Setu.
 * Each entry represents a reported need from a community member or NGO.
 */

export const CATEGORIES = {
  FOOD: "Food & Nutrition",
  MEDICAL: "Medical Aid",
  EDUCATION: "Education",
  SHELTER: "Shelter",
  ELDERLY: "Elderly Care",
  DISABILITY: "Disability Support",
  DISASTER: "Disaster Relief",
};

export const URGENCY = {
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
  CRITICAL: "Critical",
};

export const STATUS = {
  OPEN: "Open",
  IN_PROGRESS: "In Progress",
  FULFILLED: "Fulfilled",
};

/** @type {Array<Need>} */
export const mockNeeds = [
  {
    id: "need-001",
    title: "Emergency Food Packets for Flood-Affected Families",
    description:
      "Over 40 families in Nandanvan locality have been displaced due to flash floods. Immediate dry ration kits are needed for at least 10 days.",
    category: CATEGORIES.FOOD,
    urgency: URGENCY.CRITICAL,
    status: STATUS.OPEN,
    resolutionWindow: "24 Hours",
    location: {
      city: "Nagpur",
      state: "Maharashtra",
      pincode: "440009",
    },
    reportedBy: "Nagpur Relief Trust",
    reportedAt: "2026-04-20T08:30:00Z",
    volunteersNeeded: 15,
    volunteersAssigned: 3,
    contactName: "Suresh Bhat",
    contactPhone: "+91-9876543210",
    tags: ["food", "flood", "urgent", "ration"],
  },
  {
    id: "need-002",
    title: "Free Medical Camp — Medicines for Diabetic Patients",
    description:
      "A rural village near Wardha lacks access to insulin and metformin. Monthly supply for ~60 patients is required. Doctors are available but medicines are scarce.",
    category: CATEGORIES.MEDICAL,
    urgency: URGENCY.HIGH,
    status: STATUS.IN_PROGRESS,
    resolutionWindow: "3 Days",
    location: {
      city: "Wardha",
      state: "Maharashtra",
      pincode: "442001",
    },
    reportedBy: "Seva Gram Health Centre",
    reportedAt: "2026-04-18T11:00:00Z",
    volunteersNeeded: 8,
    volunteersAssigned: 5,
    contactName: "Dr. Meena Kulkarni",
    contactPhone: "+91-9823456789",
    tags: ["medical", "diabetes", "medicines", "rural"],
  },
  {
    id: "need-003",
    title: "Tutors Needed for Class 10 Students — Board Exam Prep",
    description:
      "Government school students from low-income families in Dharavi need volunteer tutors for Maths, Science, and English for upcoming board exams.",
    category: CATEGORIES.EDUCATION,
    urgency: URGENCY.MEDIUM,
    status: STATUS.OPEN,
    resolutionWindow: "7 Days",
    location: {
      city: "Mumbai",
      state: "Maharashtra",
      pincode: "400017",
    },
    reportedBy: "Akanksha Foundation",
    reportedAt: "2026-04-15T09:00:00Z",
    volunteersNeeded: 20,
    volunteersAssigned: 9,
    contactName: "Priya Sharma",
    contactPhone: "+91-9912345678",
    tags: ["education", "tutoring", "board exams", "youth"],
  },
  {
    id: "need-004",
    title: "Temporary Shelter Setup for Migrant Workers",
    description:
      "Around 200 migrant workers stranded after construction project shutdown. Need tarpaulin sheets, blankets, and basic sanitation units.",
    category: CATEGORIES.SHELTER,
    urgency: URGENCY.HIGH,
    status: STATUS.OPEN,
    resolutionWindow: "3 Days",
    location: {
      city: "Pune",
      state: "Maharashtra",
      pincode: "411027",
    },
    reportedBy: "PUCL Pune",
    reportedAt: "2026-04-21T14:00:00Z",
    volunteersNeeded: 25,
    volunteersAssigned: 10,
    contactName: "Ramesh Jadhav",
    contactPhone: "+91-9988776655",
    tags: ["shelter", "migrant workers", "sanitation"],
  },
  {
    id: "need-005",
    title: "Weekly Grocery Delivery for Bedridden Elderly",
    description:
      "12 senior citizens (70+) living alone in Sadashiv Peth need weekly grocery and medicine delivery support. Most are immobile.",
    category: CATEGORIES.ELDERLY,
    urgency: URGENCY.MEDIUM,
    status: STATUS.IN_PROGRESS,
    resolutionWindow: "7 Days",
    location: {
      city: "Pune",
      state: "Maharashtra",
      pincode: "411030",
    },
    reportedBy: "HelpAge India — Pune Chapter",
    reportedAt: "2026-04-10T10:30:00Z",
    volunteersNeeded: 6,
    volunteersAssigned: 6,
    contactName: "Sunita Deshpande",
    contactPhone: "+91-9765432109",
    tags: ["elderly", "delivery", "grocery", "medicine"],
  },
  {
    id: "need-006",
    title: "Wheelchair & Assistive Device Distribution",
    description:
      "30 individuals with mobility impairments across Solapur district need wheelchairs, crutches, and hearing aids. Funds are available but logistics volunteers are missing.",
    category: CATEGORIES.DISABILITY,
    urgency: URGENCY.LOW,
    status: STATUS.OPEN,
    resolutionWindow: "7 Days",
    location: {
      city: "Solapur",
      state: "Maharashtra",
      pincode: "413001",
    },
    reportedBy: "Divyangjan Welfare Society",
    reportedAt: "2026-04-12T13:00:00Z",
    volunteersNeeded: 10,
    volunteersAssigned: 2,
    contactName: "Anil Patil",
    contactPhone: "+91-9823001122",
    tags: ["disability", "wheelchair", "assistive devices", "logistics"],
  },
  {
    id: "need-007",
    title: "Cyclone Relief — Clothes & Utensils for 500 Families",
    description:
      "Cyclone-affected coastal village of Vengurla requires immediate supply of clothing (all sizes), steel utensils, and cooking essentials for displaced families.",
    category: CATEGORIES.DISASTER,
    urgency: URGENCY.CRITICAL,
    status: STATUS.OPEN,
    resolutionWindow: "24 Hours",
    location: {
      city: "Vengurla",
      state: "Maharashtra",
      pincode: "416516",
    },
    reportedBy: "Maharashtra State Disaster Management Authority",
    reportedAt: "2026-04-22T06:00:00Z",
    volunteersNeeded: 50,
    volunteersAssigned: 12,
    contactName: "Collector Office Sindhudurg",
    contactPhone: "+91-2362-272222",
    tags: ["cyclone", "disaster", "clothes", "relief"],
  },
  {
    id: "need-008",
    title: "Midday Meal Volunteers for Tribal School",
    description:
      "An ashram school in Melghat tribal area needs daily volunteers to assist in cooking and serving midday meals for 150 students.",
    category: CATEGORIES.FOOD,
    urgency: URGENCY.LOW,
    status: STATUS.FULFILLED,
    resolutionWindow: "7 Days",
    location: {
      city: "Amravati",
      state: "Maharashtra",
      pincode: "444601",
    },
    reportedBy: "Korku Seva Mandal",
    reportedAt: "2026-04-05T08:00:00Z",
    volunteersNeeded: 5,
    volunteersAssigned: 5,
    contactName: "Vandana Bhosale",
    contactPhone: "+91-9870123456",
    tags: ["food", "tribal", "school", "midday meal"],
  },
];

export default mockNeeds;
