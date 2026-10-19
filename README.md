# 🌿 ChefMint AI
> **Multimodal AI-Powered Zero-Waste Culinary Copilot & Intelligent Meal Planner**  
> *Submitted to EurekaDEV 2026 — Coding Track (Computer Science + AI)*

## 📌 The Problem & Solution
Global households waste over 1 billion meals daily due to decision fatigue with leftover ingredients (UNEP Food Waste Index). **ChefMint AI** transforms fridge photos into structured, actionable, zero-waste recipes instantly.

## 🚀 Key Features
- **Visual Fridge Scanner:** Upload fridge/pantry photos processed by NVIDIA multi-modal vision models.
- **Interactive Ingredient Chips:** Automatically converts detected items into editable, removable visual chips (`st.session_state`).
- **Custom Filters:** Tailor recipes by Meal Type, Cuisine Style, and custom notes.
- **Zero-Waste Recipes:** Generates recipe cards with prep times, calorie metrics, and missing pantry staples.

## 🛠️ Tech Stack & Architecture
- **Frontend/UI:** Streamlit (Python)
- **Vision Model:** `nvidia/nemotron-3.5-super-vl` (via Nebius Token Factory)
- **Reasoning Model:** `nvidia/Llama-3.1-Nemotron-70B-Instruct` (via Nebius Token Factory)

## ⚙️ Setup & Local Execution
1. Clone repository and install dependencies: `pip install -r requirements.txt`
2. Run app: `streamlit run app.py`

## 📚 Citations
1. United Nations Environment Programme (UNEP). *Food Waste Index Report 2024.*
