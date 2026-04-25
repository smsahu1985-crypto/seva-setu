# SevaSetu Volunteer Recommendation Engine

AI-powered volunteer-task matching system for NGOs.

Built for hackathon project **SevaSetu**.

---

## Problem Solved

NGOs often struggle to assign the right volunteers to the right tasks.

This engine intelligently recommends tasks to volunteers using:

- Skills match
- Distance
- Priority of task
- Urgency / deadline
- Vehicle availability
- Language compatibility
- Experience level
- Reliability score
- Workload balancing

---

## Model Used

LightGBM LambdaRank

Why?

- Designed for ranking problems
- Better than simple classification
- Fast training
- Great for recommendation systems

---

## Project Structure

recommendation_ai/
│── train.py  
│── recommend.py  
│── generate_dataset.py  
│── app.py  
│── models/  
│   ├── lgbm_ranker.pkl  
│   └── model_meta.json  

---

## Installation

```bash
pip install -r requirements.txt