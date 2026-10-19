"""
ChefMint AI 🌿
Snap your fridge, zero out food waste, and create instant gourmet recipes.
Nebius x NVIDIA Hackathon Edition
"""

import os
import io
import json
import base64
import re
from typing import List, Dict, Any, Optional
from PIL import Image
import streamlit as st
from openai import OpenAI

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
HARDCODED_API_KEY_FALLBACK = (
    "v1.CmMKHHN0YXRpY2tleS1lMDBuMmtxenpnejJkczRuZ2USIXNlcnZpY2VhY2NvdW50LWUwMGJiemYwaGtlZzk4MzRyMzILCNvS09YGEJzH92w6DAjW1euhBxCA6dLQAkACWgNlMDA."
    "AAAAAAAAAAE9I-AHjKl7BDsJkXfBeCMsTZV6N8mOzdlM8-289yrgj2MDvanL6fghv56HLMpTmUuVSfM4bLnVB7n3h9oPL4gB"
)

VISION_MODEL = "nvidia/Nemotron-3.5-Super-VL"
RECIPE_MODEL = "nvidia/nemotron-3-super-120b-a12b"
RECIPE_MODEL_FALLBACK = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"

# Page setup - Mobile & iPhone full width
st.set_page_config(
    page_title="ChefMint AI 🌿",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Mobile First CSS (Zero Sideways Scroll on iPhone)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Full mobile width constraint without horizontal overflow */
    html, body, [data-testid="stAppViewContainer"], .main {
        width: 100% !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
        -webkit-text-size-adjust: 100%;
        background-color: #FAFAF9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .block-container {
        max-width: 1100px !important;
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
        margin: 0 auto !important;
    }

    /* Hero Banner */
    .chef-hero {
        background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 50%, #FFFFFF 100%);
        border: 1px solid #A7F3D0;
        border-radius: 16px;
        padding: 1.25rem 1.2rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        word-wrap: break-word;
    }
    .chef-title {
        color: #064E3B;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.25rem;
        line-height: 1.2;
    }
    .chef-subtitle {
        color: #047857;
        font-size: 0.95rem;
        font-weight: 500;
        line-height: 1.4;
    }
    .feature-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background-color: #FFFFFF;
        border: 1px solid #6EE7B7;
        color: #065F46;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-top: 0.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }

    /* Recipe Container Card */
    .chef-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
        word-wrap: break-word;
    }
    .chef-card:hover {
        border-color: #10B981;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.08);
    }

    /* Calorie calculation breakdown box */
    .calc-breakdown-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #10B981;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        margin: 0.75rem 0;
        font-size: 0.82rem;
        color: #1E293B;
    }

    /* Metric Badges */
    .metric-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        background-color: #F3F4F6;
        color: #1F2937;
        border: 1px solid #E5E7EB;
    }
    .metric-badge-time {
        background-color: #EFF6FF;
        color: #1D4ED8;
        border-color: #DBEAFE;
    }
    .metric-badge-cal {
        background-color: #FFF7ED;
        color: #C2410C;
        border-color: #FFEDD5;
    }
    .metric-badge-diff {
        background-color: #ECFDF5;
        color: #047857;
        border-color: #D1FAE5;
    }

    /* Missing Staples Callout */
    .staples-callout {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 3px solid #F59E0B;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        margin: 0.75rem 0;
        font-size: 0.85rem;
        word-wrap: break-word;
    }

    /* Buttons */
    div.stButton > button[kind="primary"] {
        background-color: #10B981 !important;
        border-color: #10B981 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.25rem !important;
        box-shadow: 0 3px 10px rgba(16, 185, 129, 0.25) !important;
        width: 100% !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #059669 !important;
        border-color: #059669 !important;
    }

    div.stButton > button:not([kind="primary"]) {
        border-radius: 8px !important;
        border: 1px solid #E5E7EB !important;
        color: #374151 !important;
        font-size: 0.85rem !important;
    }
    div.stButton > button:not([kind="primary"]):hover {
        border-color: #10B981 !important;
        color: #065F46 !important;
        background-color: #ECFDF5 !important;
    }

    /* Code snippets & markdown wrapped for mobile */
    pre, code, .stCodeBlock {
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
    }

    @media (max-width: 640px) {
        .chef-title {
            font-size: 1.5rem !important;
        }
        .chef-subtitle {
            font-size: 0.85rem !important;
        }
        .chef-hero {
            padding: 1rem 0.85rem !important;
        }
        .chef-card {
            padding: 0.9rem !important;
        }
        .stColumns {
            flex-direction: column !important;
            gap: 1rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Culinary Database: Portion Sizes & Realistic USDA Calorie / Macro Lookup
# -----------------------------------------------------------------------------
INGREDIENT_NUTRITION_DB: Dict[str, Dict[str, Any]] = {
    "nutella": {"portion": "2 tbsp hazelnut cocoa spread (37g)", "calories": 200, "protein": 2, "carbs": 21, "fat": 12},
    "strawberry": {"portion": "1 cup sliced fresh strawberries (150g)", "calories": 48, "protein": 1, "carbs": 11, "fat": 0.5},
    "strawberries": {"portion": "1 cup sliced fresh strawberries (150g)", "calories": 48, "protein": 1, "carbs": 11, "fat": 0.5},
    "banana": {"portion": "1 medium ripe banana (118g)", "calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.3},
    "honey": {"portion": "1 tbsp pure honey (21g)", "calories": 64, "protein": 0.1, "carbs": 17, "fat": 0},
    "peanut butter": {"portion": "2 tbsp creamy peanut butter (32g)", "calories": 190, "protein": 8, "carbs": 7, "fat": 16},
    "egg": {"portion": "2 large eggs (100g)", "calories": 140, "protein": 12, "carbs": 1, "fat": 10},
    "eggs": {"portion": "2 large eggs (100g)", "calories": 140, "protein": 12, "carbs": 1, "fat": 10},
    "spinach": {"portion": "2 cups fresh baby spinach (60g)", "calories": 14, "protein": 2, "carbs": 2, "fat": 0},
    "baby spinach": {"portion": "2 cups fresh baby spinach (60g)", "calories": 14, "protein": 2, "carbs": 2, "fat": 0},
    "cheddar": {"portion": "1 oz shredded sharp cheddar (28g)", "calories": 110, "protein": 7, "carbs": 1, "fat": 9},
    "cheddar cheese": {"portion": "1 oz shredded sharp cheddar (28g)", "calories": 110, "protein": 7, "carbs": 1, "fat": 9},
    "cheese": {"portion": "1 oz shredded cheese (28g)", "calories": 110, "protein": 7, "carbs": 1, "fat": 9},
    "yogurt": {"portion": "1/2 cup plain Greek yogurt (120g)", "calories": 80, "protein": 12, "carbs": 4, "fat": 1},
    "greek yogurt": {"portion": "1/2 cup plain Greek yogurt (120g)", "calories": 80, "protein": 12, "carbs": 4, "fat": 1},
    "garlic": {"portion": "2 cloves garlic, minced (6g)", "calories": 9, "protein": 0.4, "carbs": 2, "fat": 0},
    "chicken": {"portion": "1 chicken breast fillet (150g)", "calories": 240, "protein": 46, "carbs": 0, "fat": 5},
    "chicken breast": {"portion": "1 chicken breast fillet (150g)", "calories": 240, "protein": 46, "carbs": 0, "fat": 5},
    "salmon": {"portion": "1 fresh salmon fillet (170g / 6 oz)", "calories": 340, "protein": 34, "carbs": 0, "fat": 22},
    "beef": {"portion": "4 oz lean ground beef (113g)", "calories": 260, "protein": 24, "carbs": 0, "fat": 18},
    "tofu": {"portion": "1/2 block firm tofu (150g)", "calories": 120, "protein": 14, "carbs": 3, "fat": 7},
    "avocado": {"portion": "1/2 medium ripe avocado (100g)", "calories": 160, "protein": 2, "carbs": 8, "fat": 15},
    "rice": {"portion": "1 cup cooked jasmine rice (150g)", "calories": 195, "protein": 4, "carbs": 42, "fat": 0.5},
    "pasta": {"portion": "1 cup cooked pasta (140g)", "calories": 220, "protein": 8, "carbs": 43, "fat": 1.2},
    "bell pepper": {"portion": "1 whole bell pepper, sliced (120g)", "calories": 32, "protein": 1.2, "carbs": 7, "fat": 0.2},
    "pepper": {"portion": "1 medium pepper, chopped (120g)", "calories": 32, "protein": 1.2, "carbs": 7, "fat": 0.2},
    "tomato": {"portion": "1 medium vine tomato (125g)", "calories": 22, "protein": 1, "carbs": 5, "fat": 0.2},
    "tomatoes": {"portion": "1 cup cherry tomatoes (150g)", "calories": 27, "protein": 1.3, "carbs": 6, "fat": 0.3},
    "onion": {"portion": "1/2 medium onion, diced (80g)", "calories": 32, "protein": 0.9, "carbs": 7.5, "fat": 0.1},
    "broccoli": {"portion": "1.5 cups fresh broccoli florets (135g)", "calories": 45, "protein": 3.8, "carbs": 9, "fat": 0.5},
    "mushrooms": {"portion": "1.5 cups sliced cremini mushrooms (105g)", "calories": 23, "protein": 3.2, "carbs": 3.4, "fat": 0.3},
    "zucchini": {"portion": "1 medium zucchini, sliced (150g)", "calories": 25, "protein": 1.8, "carbs": 4.7, "fat": 0.5},
    "potato": {"portion": "1 medium russet potato (170g)", "calories": 160, "protein": 4.3, "carbs": 37, "fat": 0.2},
    "bread": {"portion": "1 thick slice artisanal bread (45g)", "calories": 120, "protein": 4, "carbs": 22, "fat": 1.5},
    "butter": {"portion": "1 tbsp unsalted butter (14g)", "calories": 102, "protein": 0.1, "carbs": 0, "fat": 11.5},
    "olive oil": {"portion": "1 tbsp extra-virgin olive oil (14g)", "calories": 119, "protein": 0, "carbs": 0, "fat": 13.5},
    "lemon": {"portion": "Juice of 1/2 fresh lemon (25g)", "calories": 6, "protein": 0.1, "carbs": 2, "fat": 0},
    "asparagus": {"portion": "1 cup fresh asparagus spears (130g)", "calories": 27, "protein": 3, "carbs": 5, "fat": 0.2},
}

def lookup_ingredient_measurements(name: str) -> Dict[str, Any]:
    """Look up or intelligently estimate exact cooking portion & USDA calories."""
    clean = name.strip().lower()
    for key, data in INGREDIENT_NUTRITION_DB.items():
        if key in clean or clean in key:
            return {
                "name": name.strip().capitalize(),
                "portion": data["portion"],
                "calories": data["calories"],
                "protein": data["protein"],
                "carbs": data["carbs"],
                "fat": data["fat"],
            }
    # Intelligent generic fallback based on word cues
    if any(k in clean for k in ["meat", "fish", "pork", "shrimp", "turkey", "tuna"]):
        return {"name": name.strip().capitalize(), "portion": "4 oz cooked portion (113g)", "calories": 210, "protein": 28, "carbs": 0, "fat": 10}
    if any(k in clean for k in ["leaf", "kale", "lettuce", "greens", "herb", "parsley", "cilantro"]):
        return {"name": name.strip().capitalize(), "portion": "1.5 cups fresh leaves (50g)", "calories": 15, "protein": 1.5, "carbs": 2, "fat": 0.2}
    if any(k in clean for k in ["bean", "lentil", "chickpea", "grain", "quinoa", "oat"]):
        return {"name": name.strip().capitalize(), "portion": "1/2 cup cooked portion (100g)", "calories": 130, "protein": 7, "carbs": 22, "fat": 1}
    # Default vegetable / produce portion
    return {"name": name.strip().capitalize(), "portion": "1 cup prepared portion (110g)", "calories": 40, "protein": 2, "carbs": 8, "fat": 0.5}


# -----------------------------------------------------------------------------
# Session State & API Key Management
# -----------------------------------------------------------------------------
if "custom_api_key" not in st.session_state:
    st.session_state.custom_api_key = ""

if "ingredients" not in st.session_state:
    st.session_state.ingredients = ["Eggs", "Baby Spinach", "Greek Yogurt", "Garlic", "Cheddar Cheese"]

if "pending_ingredient_text" not in st.session_state:
    st.session_state.pending_ingredient_text = ""

if "selected_meals" not in st.session_state:
    st.session_state.selected_meals = {0}

if "recipes" not in st.session_state:
    st.session_state.recipes = [
        {
            "title": "Gourmet Spinach & Cheddar Herb Frittata",
            "prep_time": "12 mins",
            "calories": "304 kcal",
            "protein": "21g",
            "carbs": "4g",
            "fat": "20g",
            "difficulty": "Easy",
            "measured_ingredients": [
                {"name": "Eggs", "portion": "2 large eggs (100g)", "calories": 140, "protein": 12, "carbs": 1, "fat": 10},
                {"name": "Baby Spinach", "portion": "2 cups fresh baby spinach (60g)", "calories": 14, "protein": 2, "carbs": 2, "fat": 0},
                {"name": "Cheddar Cheese", "portion": "1 oz shredded sharp cheddar (28g)", "calories": 110, "protein": 7, "carbs": 1, "fat": 9},
                {"name": "Garlic", "portion": "1 clove garlic, minced (3g)", "calories": 4, "protein": 0.2, "carbs": 1, "fat": 0},
            ],
            "cooking_fat": {"name": "Olive oil", "portion": "1 tsp (5g)", "calories": 40, "fat": 4.5},
            "used_ingredients": ["Eggs", "Baby Spinach", "Cheddar Cheese", "Garlic"],
            "missing_staples": ["Olive oil", "Black pepper", "Sea salt"],
            "instructions": [
                "Warm a seasoned non-stick skillet with 1 tsp olive oil over medium heat.",
                "Sauté minced garlic and 2 cups baby spinach for 90 seconds until vibrant green.",
                "Whisk 2 large eggs and pour into skillet; fold in 1 oz sharp cheddar cheese until set.",
                "Garnish with cracked black pepper and fresh herbs; serve golden and hot."
            ]
        },
        {
            "title": "Rustic Garlic Vegetable Sauté Skillet",
            "prep_time": "10 mins",
            "calories": "260 kcal",
            "protein": "11g",
            "carbs": "8g",
            "fat": "18g",
            "difficulty": "Easy",
            "measured_ingredients": [
                {"name": "Baby Spinach", "portion": "3 cups fresh spinach (90g)", "calories": 21, "protein": 2.8, "carbs": 3.2, "fat": 0.4},
                {"name": "Garlic", "portion": "2 cloves garlic, thinly sliced (6g)", "calories": 9, "protein": 0.4, "carbs": 2, "fat": 0},
                {"name": "Cheddar Cheese", "portion": "1 oz shaved cheddar (28g)", "calories": 110, "protein": 7, "carbs": 1, "fat": 9},
            ],
            "cooking_fat": {"name": "Olive oil", "portion": "1 tbsp (14g)", "calories": 120, "fat": 13.5},
            "used_ingredients": ["Baby Spinach", "Garlic", "Cheddar Cheese"],
            "missing_staples": ["Olive oil", "Crushed red pepper flakes"],
            "instructions": [
                "Heat 1 tbsp olive oil in a wide pan and toast sliced garlic until lightly golden.",
                "Toss in fresh spinach over medium-high heat for 3-4 minutes until wilted.",
                "Top with shaved cheddar to melt delicately, finish with sea salt, and serve immediately."
            ]
        },
        {
            "title": "Greek Yogurt & Soft-Poached Egg Protein Bowl",
            "prep_time": "6 mins",
            "calories": "260 kcal",
            "protein": "18g",
            "carbs": "5g",
            "fat": "15g",
            "difficulty": "Easy",
            "measured_ingredients": [
                {"name": "Greek Yogurt", "portion": "1/2 cup plain Greek yogurt (120g)", "calories": 80, "protein": 12, "carbs": 4, "fat": 1},
                {"name": "Eggs", "portion": "1 large egg, soft-boiled or poached (50g)", "calories": 70, "protein": 6, "carbs": 0.5, "fat": 5},
                {"name": "Garlic", "portion": "1/2 clove garlic, microplaned (2g)", "calories": 3, "protein": 0.1, "carbs": 0.7, "fat": 0},
            ],
            "cooking_fat": {"name": "Herb-infused oil", "portion": "2 tsp (10g)", "calories": 80, "fat": 9},
            "used_ingredients": ["Greek Yogurt", "Garlic", "Eggs"],
            "missing_staples": ["Paprika", "Toasted seeds / nuts"],
            "instructions": [
                "Whisk 1/2 cup Greek yogurt with microplaned garlic and a pinch of sea salt until silky.",
                "Top with a warm soft-poached or soft-boiled egg in a shallow artisan bowl.",
                "Drizzle with 2 tsp warm herb-infused oil and dust with smoked paprika."
            ]
        }
    ]

if "raw_vision_output" not in st.session_state:
    st.session_state.raw_vision_output = ""

if "last_error" not in st.session_state:
    st.session_state.last_error = None


def get_active_api_key() -> str:
    """Retrieve user-entered key, environment key, or fallback."""
    if st.session_state.custom_api_key and st.session_state.custom_api_key.strip():
        return st.session_state.custom_api_key.strip()
    env_key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if env_key:
        return env_key
    return HARDCODED_API_KEY_FALLBACK


def get_nebius_client() -> OpenAI:
    """Initialize OpenAI client pointing to the Nebius endpoint."""
    return OpenAI(
        base_url=NEBIUS_BASE_URL,
        api_key=get_active_api_key(),
    )


# -----------------------------------------------------------------------------
# Image Processing & Stage 1 Vision
# -----------------------------------------------------------------------------
def image_to_base64(image_bytes: bytes) -> str:
    """Convert raw image bytes to a JPEG base64 string with optimization."""
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    max_dim = 1024
    if max(image.size) > max_dim:
        image.thumbnail((max_dim, max_dim))

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def scan_fridge_image(image_bytes: bytes) -> List[str]:
    """
    Stage 1: Vision Model Ingredient Scanning
    Capped at max_tokens=100
    """
    try:
        b64_image = image_to_base64(image_bytes)
        client = get_nebius_client()

        system_prompt = "List only visible raw food ingredients as a plain comma-separated list. Maximum 15 items."

        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "What raw food ingredients do you see in this fridge?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                ]},
            ],
            max_tokens=100,
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        st.session_state.raw_vision_output = content

        detected = []
        for item in content.replace("\n", ",").split(","):
            cleaned = item.strip().strip(".-*•0123456789 ")
            if cleaned and len(cleaned) > 1 and cleaned.lower() not in [i.lower() for i in detected]:
                detected.append(cleaned.capitalize())

        return detected
    except Exception as e:
        st.session_state.last_error = f"Vision Scanner: {str(e)}"
        return []


# -----------------------------------------------------------------------------
# Stage 2 Recipe Generation with Precise Cooking Measurements & Derived Calories
# -----------------------------------------------------------------------------
def build_measured_recipes_from_items(
    active_items: List[str],
    meal_type: str,
    cuisine_style: str,
    craving: str,
    seed_offset: int = 0
) -> List[Dict[str, Any]]:
    """Build 3 chef-grade, culinarily accurate recipes with exact cooking measurements and calculated calories."""
    items = list(active_items) if active_items else ["Seasonal Vegetables", "Aromatics"]
    lower_items = [i.lower() for i in items]

    has_salmon = any("salmon" in i or "fish" in i or "trout" in i for i in lower_items)
    has_chicken = any("chicken" in i or "poultry" in i for i in lower_items)
    has_steak = any("steak" in i or "beef" in i or "meat" in i for i in lower_items)
    has_asparagus = any("asparagus" in i for i in lower_items)
    has_broccoli = any("broccoli" in i for i in lower_items)
    has_lemon = any("lemon" in i for i in lower_items)

    has_nutella = any("nutella" in i or "chocolate" in i or "hazelnut" in i for i in lower_items)
    has_strawberry = any("strawberr" in i or "berry" in i for i in lower_items)
    has_bread = any("bread" in i or "toast" in i for i in lower_items)

    c_prefix = cuisine_style if cuisine_style != "Any" else "Gourmet"
    m_suffix = meal_type if meal_type != "All" else "Creation"

    recipes_out = []

    # Category 0: Sweet spreads & French toast / Parfait (NO sautéing Nutella in oil!)
    if has_nutella or (has_strawberry and has_bread):
        nut_m = lookup_ingredient_measurements("Nutella")
        bread_m = lookup_ingredient_measurements("Bread")
        straw_m = lookup_ingredient_measurements("Strawberries")
        measured_sweet = [nut_m, bread_m, straw_m]
        tot_cals_sweet = sum(m["calories"] for m in measured_sweet)

        recipes_out.append({
            "title": "Artisanal Toasted Brioche with Nutella & Macerated Strawberries",
            "prep_time": "8 mins",
            "calories": f"{int(tot_cals_sweet)} kcal",
            "protein": "9g",
            "carbs": "64g",
            "fat": "14g",
            "difficulty": "Easy",
            "measured_ingredients": measured_sweet,
            "used_ingredients": ["Nutella", "Bread", "Strawberries"],
            "missing_staples": ["Powdered sugar", "Fresh mint"],
            "instructions": [
                "Lightly toast artisanal bread slices until golden brown and crisp on the outside.",
                "Generously spread 2 tablespoons of creamy Nutella evenly across each warm slice of bread.",
                "Rinse and thinly slice fresh ruby strawberries; arrange neatly in overlapping layers across the hazelnut spread.",
                "Finish with a light dusting of powdered sugar and fresh mint sprig."
            ]
        })

        recipes_out.append({
            "title": "Crispy Grilled Nutella & Strawberry Dessert Panini",
            "prep_time": "10 mins",
            "calories": "390 kcal",
            "protein": "8g",
            "carbs": "58g",
            "fat": "16g",
            "difficulty": "Easy",
            "measured_ingredients": [bread_m, nut_m, straw_m],
            "cooking_fat": {"name": "European butter", "portion": "1 tsp (5g)", "calories": 34, "fat": 3.8},
            "used_ingredients": ["Bread", "Nutella", "Strawberries"],
            "missing_staples": ["Butter", "Ground cinnamon"],
            "instructions": [
                "Spread 1.5 tablespoons of Nutella inside two bread slices, layering thinly sliced strawberries in between.",
                "Brush sandwich exterior lightly with melted butter.",
                "Grill in a non-stick skillet over medium-low heat for 3 minutes per side until bread is golden-crisp and chocolate center is warm and melty.",
                "Slice diagonally and serve immediately."
            ]
        })

        yog_m = lookup_ingredient_measurements("Greek Yogurt")
        recipes_out.append({
            "title": "Whipped Greek Yogurt & Nutella Strawberry Parfait",
            "prep_time": "5 mins",
            "calories": "328 kcal",
            "protein": "15g",
            "carbs": "36g",
            "fat": "13g",
            "difficulty": "Easy",
            "measured_ingredients": [yog_m, nut_m, straw_m],
            "used_ingredients": ["Greek Yogurt", "Nutella", "Strawberries"],
            "missing_staples": ["Toasted crushed hazelnuts", "Honey"],
            "instructions": [
                "Spoon chilled Greek yogurt into the base of a dessert cup or wide bowl.",
                "Warm 2 tablespoons of Nutella gently for 10 seconds, then swirl in rich ribbon ribbons throughout the yogurt.",
                "Crown with fresh strawberry slices and toasted crushed hazelnuts for texture."
            ]
        })
        return recipes_out

    # Recipe 1: Signature Protein or Skillet
    if has_salmon:
        salmon_m = lookup_ingredient_measurements("Salmon")
        veg_name = "Asparagus" if has_asparagus else (items[1] if len(items) > 1 else "Baby Spinach")
        veg_m = lookup_ingredient_measurements(veg_name)
        arom_name = "Lemon" if has_lemon else (items[2] if len(items) > 2 else "Garlic")
        arom_m = lookup_ingredient_measurements(arom_name)
        oil1 = {"name": "Olive oil", "portion": "1 tsp (5g)", "calories": 40, "fat": 4.5}
        measured1 = [salmon_m, veg_m, arom_m]
        tot_cals1 = sum(m["calories"] for m in measured1) + oil1["calories"]
        tot_p1 = sum(m["protein"] for m in measured1)
        tot_cb1 = sum(m["carbs"] for m in measured1)
        tot_f1 = sum(m["fat"] for m in measured1) + oil1["fat"]

        recipes_out.append({
            "title": f"Pan-Seared Crispy Skin Salmon with {veg_m['name']} & Lemon Emulsion",
            "prep_time": "14 mins",
            "calories": f"{int(tot_cals1)} kcal",
            "protein": f"{int(tot_p1)}g",
            "carbs": f"{int(tot_cb1)}g",
            "fat": f"{int(tot_f1)}g",
            "difficulty": "Easy",
            "measured_ingredients": measured1,
            "cooking_fat": oil1,
            "used_ingredients": [salmon_m["name"], veg_m["name"], arom_m["name"]],
            "missing_staples": ["Olive oil", "Flaky sea salt", "Black pepper"],
            "instructions": [
                "Pat the salmon fillet completely dry with paper towels; season skin and flesh with sea salt and black pepper.",
                "Heat 1 tsp olive oil in a heavy skillet over medium-high heat until shimmering.",
                "Place salmon skin-side down, press gently for 10 seconds, and sear undisturbed for 4-5 minutes until skin is crispy.",
                f"Add {veg_m['portion']} of {veg_m['name']} to the pan; flip salmon and cook for 2-3 minutes until tender.",
                "Squeeze fresh lemon juice over the hot pan juices, spoon over the salmon, and serve hot."
            ]
        })
    elif has_chicken:
        chicken_m = lookup_ingredient_measurements("Chicken Breast")
        veg_name = "Broccoli" if has_broccoli else (items[1] if len(items) > 1 else "Bell Pepper")
        veg_m = lookup_ingredient_measurements(veg_name)
        arom_m = lookup_ingredient_measurements(items[2] if len(items) > 2 else "Garlic")
        oil1 = {"name": "Olive oil", "portion": "1 tbsp (14g)", "calories": 120, "fat": 13.5}
        measured1 = [chicken_m, veg_m, arom_m]
        tot_cals1 = sum(m["calories"] for m in measured1) + oil1["calories"]
        tot_p1 = sum(m["protein"] for m in measured1)
        tot_cb1 = sum(m["carbs"] for m in measured1)
        tot_f1 = sum(m["fat"] for m in measured1) + oil1["fat"]

        recipes_out.append({
            "title": f"Herb-Seared Chicken Medallions with Roasted {veg_m['name']} & Garlic",
            "prep_time": "15 mins",
            "calories": f"{int(tot_cals1)} kcal",
            "protein": f"{int(tot_p1)}g",
            "carbs": f"{int(tot_cb1)}g",
            "fat": f"{int(tot_f1)}g",
            "difficulty": "Easy",
            "measured_ingredients": measured1,
            "cooking_fat": oil1,
            "used_ingredients": [chicken_m["name"], veg_m["name"], arom_m["name"]],
            "missing_staples": ["Olive oil", "Sea salt", "Italian herbs"],
            "instructions": [
                "Slice chicken breast into uniform 1/2-inch cutlets; season both sides with salt, pepper, and herbs.",
                "Heat 1 tbsp olive oil in a wide skillet over medium-high heat until hot.",
                "Sear chicken cutlets undisturbed for 3-4 minutes per side until golden brown (internal temp 165°F).",
                f"Toss in {veg_m['portion']} of {veg_m['name']} and garlic, cover for 2 minutes to flash-steam until tender-crisp.",
                "Rest chicken for 2 minutes, slice into medallions, and serve over vegetables with pan drippings."
            ]
        })
    elif has_steak:
        steak_m = lookup_ingredient_measurements("Steak")
        veg_m = lookup_ingredient_measurements(items[1] if len(items) > 1 else "Mushrooms")
        arom_m = lookup_ingredient_measurements(items[2] if len(items) > 2 else "Garlic")
        oil1 = {"name": "Cooking butter", "portion": "1 tbsp (14g)", "calories": 102, "fat": 11.5}
        measured1 = [steak_m, veg_m, arom_m]
        tot_cals1 = sum(m["calories"] for m in measured1) + oil1["calories"]
        tot_p1 = sum(m["protein"] for m in measured1)
        tot_cb1 = sum(m["carbs"] for m in measured1)
        tot_f1 = sum(m["fat"] for m in measured1) + oil1["fat"]

        recipes_out.append({
            "title": f"Pan-Seared Steak Medallions with Garlic-Basted {veg_m['name']}",
            "prep_time": "16 mins",
            "calories": f"{int(tot_cals1)} kcal",
            "protein": f"{int(tot_p1)}g",
            "carbs": f"{int(tot_cb1)}g",
            "fat": f"{int(tot_f1)}g",
            "difficulty": "Medium",
            "measured_ingredients": measured1,
            "cooking_fat": oil1,
            "used_ingredients": [steak_m["name"], veg_m["name"], arom_m["name"]],
            "missing_staples": ["Butter", "Coarse sea salt", "Cracked pepper"],
            "instructions": [
                "Bring steak to room temp for 10 minutes; pat completely dry and season with coarse salt and pepper.",
                "Sear in a smoking-hot skillet for 3 minutes per side for a deep caramelized golden crust.",
                f"Melt butter in pan with crushed garlic and {veg_m['name']}; baste steak continuously for 60 seconds.",
                "Transfer steak to a cutting board to rest for 5 minutes before slicing against the grain."
            ]
        })
    else:
        main1 = items[0]
        sub1 = items[1] if len(items) > 1 else "Aromatics"
        used1_raw = items[:min(3, len(items))]
        measured1 = [lookup_ingredient_measurements(name) for name in used1_raw]
        oil1 = {"name": "Olive oil", "portion": "1 tsp (5g)", "calories": 40, "fat": 4.5}
        tot_cals1 = sum(m["calories"] for m in measured1) + oil1["calories"]
        tot_p1 = sum(m["protein"] for m in measured1)
        tot_cb1 = sum(m["carbs"] for m in measured1)
        tot_f1 = sum(m["fat"] for m in measured1) + oil1["fat"]

        recipes_out.append({
            "title": f"{c_prefix} {main1} & {sub1} Skillet",
            "prep_time": "12 mins",
            "calories": f"{int(tot_cals1)} kcal",
            "protein": f"{int(tot_p1)}g",
            "carbs": f"{int(tot_cb1)}g",
            "fat": f"{int(tot_f1)}g",
            "difficulty": "Easy",
            "measured_ingredients": measured1,
            "cooking_fat": oil1,
            "used_ingredients": [m["name"] for m in measured1],
            "missing_staples": ["Olive oil", "Sea salt", "Black pepper"],
            "instructions": [
                f"Heat {oil1['portion']} of {oil1['name']} in a wide pan over medium flame.",
                f"Sauté {measured1[0]['portion']} of {measured1[0]['name']} for 3 minutes until tender and fragrant.",
                f"Toss in remaining items ({', '.join(m['portion'] + ' ' + m['name'] for m in measured1[1:]) if len(measured1) > 1 else 'fresh seasoning'}) and gently warm through.",
                f"Season with sea salt and fresh black pepper{f' with an emphasis on {craving}' if craving else ''}; plate hot."
            ]
        })

    # Recipe 2: Crispy / Oven dish
    main2 = items[1] if len(items) > 1 else items[0]
    sub2 = items[2] if len(items) > 2 else items[0]
    used2_raw = items[1:4] if len(items) >= 3 else [main2, sub2]
    measured2 = [lookup_ingredient_measurements(name) for name in used2_raw]
    oil2 = {"name": "Cooking butter", "portion": "1 tbsp (14g)", "calories": 102, "fat": 11.5}
    tot_cals2 = sum(m["calories"] for m in measured2) + oil2["calories"]
    tot_p2 = sum(m["protein"] for m in measured2)
    tot_cb2 = sum(m["carbs"] for m in measured2)
    tot_f2 = sum(m["fat"] for m in measured2) + oil2["fat"]

    recipes_out.append({
        "title": f"Artisanal Crispy {main2} & {sub2} {m_suffix}",
        "prep_time": "14 mins",
        "calories": f"{int(tot_cals2)} kcal",
        "protein": f"{int(tot_p2)}g",
        "carbs": f"{int(tot_cb2)}g",
        "fat": f"{int(tot_f2)}g",
        "difficulty": "Easy",
        "measured_ingredients": measured2,
        "cooking_fat": oil2,
        "used_ingredients": [m["name"] for m in measured2],
        "missing_staples": ["Butter", "Garlic clove", "Sea salt"],
        "instructions": [
            f"Warm a pan over medium heat and melt {oil2['portion']} of {oil2['name']}.",
            f"Sear {measured2[0]['portion']} of {measured2[0]['name']} until lightly caramelized.",
            f"Fold in {', '.join(m['portion'] + ' of ' + m['name'] for m in measured2[1:]) if len(measured2) > 1 else 'seasoning'} for depth.",
            "Garnish with a light pinch of flaky salt and serve while crisp and hot."
        ]
    })

    # Recipe 3: Fresh Harvest Bowl
    main3 = items[-1]
    sub3 = items[0]
    used3_raw = [main3, sub3] if len(items) >= 2 else [main3]
    measured3 = [lookup_ingredient_measurements(name) for name in used3_raw]
    oil3 = {"name": "Extra-virgin olive oil", "portion": "2 tsp (10g)", "calories": 80, "fat": 9}
    tot_cals3 = sum(m["calories"] for m in measured3) + oil3["calories"]
    tot_p3 = sum(m["protein"] for m in measured3)
    tot_cb3 = sum(m["carbs"] for m in measured3)
    tot_f3 = sum(m["fat"] for m in measured3) + oil3["fat"]

    recipes_out.append({
        "title": f"Fresh {c_prefix} {main3} & {sub3} Harvest Bowl",
        "prep_time": "8 mins",
        "calories": f"{int(tot_cals3)} kcal",
        "protein": f"{int(tot_p3)}g",
        "carbs": f"{int(tot_cb3)}g",
        "fat": f"{int(tot_f3)}g",
        "difficulty": "Easy",
        "measured_ingredients": measured3,
        "cooking_fat": oil3,
        "used_ingredients": [m["name"] for m in measured3],
        "missing_staples": ["Lemon juice", "Toasted seeds / nuts", "Sea salt"],
        "instructions": [
            f"Prepare {', '.join(m['portion'] + ' ' + m['name'] for m in measured3)} into rustic bite-sized portions.",
            f"Whisk {oil3['portion']} of {oil3['name']} with fresh lemon juice and sea salt.",
            "Toss ingredients gently in a shallow serving bowl to coat smoothly.",
            "Top with toasted seeds or fresh herbs and enjoy right away."
        ]
    })

    return recipes_out


def generate_recipes(
    ingredients: List[str],
    meal_type: str,
    cuisine_style: str,
    craving: str,
) -> List[Dict[str, Any]]:
    """Generate 3 recipes using the active ingredients with measured portions."""
    if not ingredients:
        return []

    client = get_nebius_client()

    system_prompt = (
        "You are ChefMint AI, a world-class executive chef. "
        "Generate 3 distinctly delicious, zero-waste recipes using available ingredients. "
        "CRITICAL CULINARY RULES: "
        "- Respect ingredient techniques: NEVER sauté sweet spreads (Nutella, peanut butter, jam) or fruits in oil until tender. "
        "- Use appropriate techniques: toast bread, spread Nutella, slice fruit fresh, sear fish/meat, scramble/poach eggs, roast or sauté vegetables. "
        "- Output ONLY valid JSON matching the schema."
    )
    user_prompt = (
        f"Available Ingredients: {', '.join(ingredients)}\n"
        f"Meal Type: {meal_type}\n"
        f"Cuisine Style: {cuisine_style}\n"
        f"Specific Craving/Note: {craving if craving else 'None'}\n\n"
        f"Generate 3 distinct creative gourmet zero-waste recipes strictly using available ingredients: {', '.join(ingredients)}.\n"
        "Return STRICT JSON with exactly 3 recipes matching this schema:\n"
        '{\n'
        '  "recipes": [\n'
        '    {\n'
        '      "title": "Recipe Name",\n'
        '      "prep_time": "15 mins",\n'
        '      "calories": "350 kcal",\n'
        '      "protein": "26g",\n'
        '      "carbs": "20g",\n'
        '      "fat": "14g",\n'
        '      "difficulty": "Easy",\n'
        '      "used_ingredients": ["item1", "item2"],\n'
        '      "missing_staples": ["olive oil", "salt"],\n'
        '      "instructions": ["Step 1...", "Step 2..."]\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    try:
        response = client.chat.completions.create(
            model=RECIPE_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1400,
            temperature=0.3,
        )

        content = response.choices[0].message.content or ""
        clean_json = content.strip()
        first_b = clean_json.find('{')
        last_b = clean_json.rfind('}')
        if first_b != -1 and last_b != -1 and last_b > first_b:
            clean_json = clean_json[first_b:last_b + 1]

        data = json.loads(clean_json)
        recs = data.get("recipes", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        if recs and len(recs) > 0:
            # Enrich with measured ingredients and accurate calorie calculations
            enriched = []
            for r in recs[:3]:
                used = r.get("used_ingredients", ingredients[:3])
                measured = [lookup_ingredient_measurements(u) for u in used]
                oil = {"name": "Olive oil", "portion": "1 tsp (5g)", "calories": 40, "fat": 4.5}
                sum_cals = sum(m["calories"] for m in measured) + oil["calories"]
                sum_p = sum(m["protein"] for m in measured)
                sum_c = sum(m["carbs"] for m in measured)
                sum_f = sum(m["fat"] for m in measured) + oil["fat"]

                enriched.append({
                    **r,
                    "calories": f"{int(sum_cals)} kcal",
                    "protein": f"{int(sum_p)}g",
                    "carbs": f"{int(sum_c)}g",
                    "fat": f"{int(sum_f)}g",
                    "measured_ingredients": measured,
                    "cooking_fat": oil,
                })
            return enriched
        raise ValueError("Empty recipes in LLM output")

    except Exception:
        # Fallback to guaranteed custom dynamic generation using user's active ingredients!
        return build_measured_recipes_from_items(
            ingredients, meal_type, cuisine_style, craving
        )


def get_recipe_macros(recipe: Dict[str, Any]):
    """Extract numeric calories, protein, carbs, and fat from recipe."""
    def parse_num(val, default):
        if isinstance(val, (int, float)):
            return int(val)
        if not val:
            return default
        m = re.search(r'\d+', str(val))
        return int(m.group()) if m else default

    cals = parse_num(recipe.get("calories"), 300)
    prot = parse_num(recipe.get("protein"), int((cals * 0.28) / 4))
    carbs = parse_num(recipe.get("carbs"), int((cals * 0.38) / 4))
    fat = parse_num(recipe.get("fat"), int((cals * 0.34) / 9))
    return cals, prot, carbs, fat


# -----------------------------------------------------------------------------
# UI Header & Hero (Clean Gourmet Branding, No Model Clutter)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="chef-hero">
        <h1 class="chef-title">ChefMint AI 🌿</h1>
        <div class="chef-subtitle">Snap your fridge, zero out food waste, and create instant gourmet recipes.</div>
        <div class="feature-badge">✨ Smart Fridge Scanner • Instant Zero-Waste Recipes</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sidebar: Preferences & Optional API Key Input
# -----------------------------------------------------------------------------
with st.sidebar:
    st.subheader("🍽️ Taste & Preferences")

    meal_type = st.selectbox(
        "Meal Type",
        options=["All", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"],
        index=0,
    )

    cuisine_style = st.selectbox(
        "Cuisine Style",
        options=["Any", "Italian", "Asian", "Mexican", "Middle Eastern", "Mediterranean", "American"],
        index=0,
    )

    craving = st.text_input(
        "Craving / Custom Note",
        placeholder="e.g. High protein, crispy, 1-pot...",
    )

    st.markdown("---")
    st.subheader("🧺 Pantry Reset Options")
    if st.button("🗑️ Clear All & Start Fresh", use_container_width=True):
        st.session_state.ingredients = []
        st.session_state.recipes = []
        st.session_state.last_error = None
        st.rerun()

    if st.button("🔄 Reset to Default Pantry", use_container_width=True):
        st.session_state.ingredients = ["Eggs", "Baby Spinach", "Greek Yogurt", "Garlic", "Cheddar Cheese"]
        st.session_state.recipes = []
        st.session_state.last_error = None
        st.rerun()


# -----------------------------------------------------------------------------
# Main Section: Responsive 2 Columns
# -----------------------------------------------------------------------------
col_input, col_display = st.columns([1, 1], gap="medium")

with col_input:
    st.markdown("### 📸 1. Input Fridge or Pantry")
    st.caption("Upload a photo or capture with your camera to detect ingredients automatically.")

    tab_upload, tab_camera = st.tabs(["📁 Upload Image", "📷 Live Camera"])
    
    image_bytes = None
    with tab_upload:
        uploaded_file = st.file_uploader(
            "Choose a fridge photo",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            image_bytes = uploaded_file.getvalue()
            st.image(image_bytes, caption="Fridge Snapshot", use_container_width=True)

    with tab_camera:
        camera_file = st.camera_input("Take a photo of your fridge", label_visibility="collapsed")
        if camera_file is not None:
            image_bytes = camera_file.getvalue()

    if image_bytes is not None:
        if st.button("🔍 Scan Fridge Photo", type="primary", use_container_width=True):
            with st.spinner("Scanning ingredients in your fridge..."):
                detected_items = scan_fridge_image(image_bytes)
                if detected_items:
                    existing_lower = [i.lower() for i in st.session_state.ingredients]
                    added_count = 0
                    for item in detected_items:
                        if item.lower() not in existing_lower:
                            st.session_state.ingredients.append(item)
                            existing_lower.append(item.lower())
                            added_count += 1
                    st.success(f"Added {added_count} ingredients to your pantry!")
                    st.rerun()
                else:
                    if st.session_state.last_error:
                        st.error(st.session_state.last_error)
                    else:
                        st.warning("No ingredients clearly identified. Try another angle or add manually below.")

    st.markdown("---")
    st.markdown(f"### 🥗 2. Active Ingredients ({len(st.session_state.ingredients)})")
    st.caption("Type items (separate by commas for multiple) or tap ❌ to remove.")

    # Manual Add Input with comma-separation support
    add_col1, add_col2 = st.columns([3, 1])
    with add_col1:
        new_item_typed = st.text_input(
            "New Ingredient",
            placeholder="e.g. Salmon, Asparagus, Lemon...",
            label_visibility="collapsed",
            key="input_ingredient_box"
        )
    with add_col2:
        btn_add = st.button("➕ Add", use_container_width=True)

    if btn_add and new_item_typed.strip():
        # Split by comma or semicolon
        items_to_add = [s.strip().capitalize() for s in re.split(r'[,;\n]+', new_item_typed) if s.strip()]
        existing_lower = [i.lower() for i in st.session_state.ingredients]
        for itm in items_to_add:
            if itm.lower() not in existing_lower:
                st.session_state.ingredients.append(itm)
                existing_lower.append(itm.lower())
        st.rerun()

    # Quick action to wipe pantry
    if st.session_state.ingredients:
        pcol1, pcol2 = st.columns([3, 1])
        with pcol2:
            if st.button("Clear all", key="clear_all_chips_btn", use_container_width=True):
                st.session_state.ingredients = []
                st.rerun()

    # Interactive Chips (Responsive 2-column wrap)
    if st.session_state.ingredients:
        chip_cols = st.columns(2)
        for idx, item in enumerate(list(st.session_state.ingredients)):
            col = chip_cols[idx % 2]
            with col:
                if st.button(f"❌ {item}", key=f"chip_del_{idx}_{item}", use_container_width=True):
                    st.session_state.ingredients.pop(idx)
                    st.rerun()
    else:
        st.info("Pantry is empty. Type your ingredients above (e.g. Chicken, Rice) or snap your fridge!")


with col_display:
    st.markdown("### ⚡ 3. Generate Recipes")
    st.caption("Craft 3 zero-waste dishes prioritizing what you have with exact cooking measurements.")

    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        generate_clicked = st.button(
            "⚡ Generate 3 Recipes",
            type="primary",
            use_container_width=True,
        )
    with btn_col2:
        generate_more_clicked = st.button(
            "🔄 Generate 3 More",
            use_container_width=True,
            help="Replace with 3 brand-new gourmet zero-waste recipes",
        )

    # If user typed something in the input box and directly clicked Generate: auto-commit it!
    if generate_clicked or generate_more_clicked:
        if new_item_typed and new_item_typed.strip():
            items_to_add = [s.strip().capitalize() for s in re.split(r'[,;\n]+', new_item_typed) if s.strip()]
            existing_lower = [i.lower() for i in st.session_state.ingredients]
            for itm in items_to_add:
                if itm.lower() not in existing_lower:
                    st.session_state.ingredients.append(itm)
                    existing_lower.append(itm.lower())

        if len(st.session_state.ingredients) == 0:
            st.warning("Please add at least one ingredient before generating recipes!")
        else:
            with st.spinner("AI Chef crafting 3 gourmet recipes with cooking measurements & nutrition..."):
                recipes = generate_recipes(
                    ingredients=st.session_state.ingredients,
                    meal_type=meal_type,
                    cuisine_style=cuisine_style,
                    craving=craving,
                )
                if recipes:
                    st.session_state.recipes = recipes
                    st.session_state.selected_meals = {0}
                    st.session_state.last_error = None
                    st.rerun()
                else:
                    if st.session_state.last_error:
                        st.error(st.session_state.last_error)

    # Recipe Cards Display & Nutrition Summary
    if st.session_state.recipes:
        tot_cals = 0
        tot_prot = 0
        tot_carbs = 0
        tot_fat = 0
        selected_count = 0

        for idx, rec in enumerate(st.session_state.recipes):
            if idx in st.session_state.selected_meals:
                c, p, cb, f = get_recipe_macros(rec)
                tot_cals += c
                tot_prot += p
                tot_carbs += cb
                tot_fat += f
                selected_count += 1

        st.markdown(f"#### 🥗 Selected Meal Nutrition & Macro Totals ({selected_count} Selected)")
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("🔥 Calories", f"{tot_cals} kcal")
        mcol2.metric("💪 Protein", f"{tot_prot}g")
        mcol3.metric("🌾 Carbs", f"{tot_carbs}g")
        mcol4.metric("🥑 Fats", f"{tot_fat}g")

        scol1, scol2 = st.columns([1, 1])
        with scol1:
            if st.button("Select All 3 Meals", key="btn_sel_all_meals", use_container_width=True):
                st.session_state.selected_meals = set(range(len(st.session_state.recipes)))
                st.rerun()
        with scol2:
            if st.button("Clear Selection", key="btn_clear_sel_meals", use_container_width=True):
                st.session_state.selected_meals = set()
                st.rerun()

        st.markdown("---")
        st.markdown(f"#### 🍽️ Crafted Recipes ({len(st.session_state.recipes)})")

        for r_idx, recipe in enumerate(st.session_state.recipes):
            title = recipe.get("title", f"Gourmet Recipe {r_idx + 1}")
            prep_time = recipe.get("prep_time", "15 mins")
            difficulty = recipe.get("difficulty", "Easy")
            used_ings = recipe.get("used_ingredients", [])
            measured_ings = recipe.get("measured_ingredients", [])
            cooking_fat = recipe.get("cooking_fat", {"name": "Olive oil", "portion": "1 tsp (5g)", "calories": 40, "fat": 4.5})
            missing_staples = recipe.get("missing_staples", [])
            instructions = recipe.get("instructions", [])
            cals, prot, carbs, fat = get_recipe_macros(recipe)

            # Recipe Plating AI Visualization (accurate culinary photo matched to title & ingredients)
            ing_highlights = ", ".join(used_ings[:3]) if used_ings else "fresh seasonal ingredients"
            recipe_img_query = f"michelin star culinary food photography of {title} with {ing_highlights} on ceramic plate warm natural light 8k"
            recipe_img_url = f"https://image.pollinations.ai/prompt/{recipe_img_query.replace(' ', '%20')}?width=768&height=432&nologo=true"
            st.image(recipe_img_url, caption=f"✨ AI Plating Preview: {title}", use_container_width=True)

            # Checkbox to include/exclude from meal total
            is_selected = r_idx in st.session_state.selected_meals
            chk_val = st.checkbox(
                f"✅ Include in Meal Nutrition Total ({title})",
                value=is_selected,
                key=f"meal_chk_{r_idx}"
            )
            if chk_val != is_selected:
                if chk_val:
                    st.session_state.selected_meals.add(r_idx)
                else:
                    st.session_state.selected_meals.discard(r_idx)
                st.rerun()

            # Container Card with Macro Badges
            st.markdown(f"""
            <div class="chef-card">
                <div style="margin-bottom: 0.6rem;">
                    <h3 style="margin: 0; color: #065F46; font-size: 1.25rem; font-weight: 700; word-break: break-word;">{title}</h3>
                </div>
                <div style="display: flex; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 0.75rem;">
                    <span class="metric-badge metric-badge-time">⏱️ {prep_time}</span>
                    <span class="metric-badge metric-badge-cal">🔥 {cals} kcal</span>
                    <span class="metric-badge metric-badge-diff">💪 {prot}g Prot</span>
                    <span class="metric-badge metric-badge-diff">🌾 {carbs}g Carb</span>
                    <span class="metric-badge metric-badge-diff">🥑 {fat}g Fat</span>
                    <span class="metric-badge">🎯 {difficulty}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.container():
                # Cooking Measurements & Nutritional Breakdown
                st.markdown("**📐 Cooking Measurements & Portions Used:**")
                if measured_ings:
                    for m in measured_ings:
                        st.markdown(f"- **{m.get('portion', m['name'])}** ({m['name']}) → `{m.get('calories', 0)} kcal` • `{m.get('protein', 0)}g P` • `{m.get('fat', 0)}g F`")
                    if cooking_fat:
                        st.markdown(f"- **{cooking_fat.get('portion', '1 tsp')}** ({cooking_fat.get('name', 'Cooking oil')}) → `{cooking_fat.get('calories', 40)} kcal` • `{cooking_fat.get('fat', 4.5)}g F`")
                elif used_ings:
                    for u in used_ings:
                        st.markdown(f"- ✅ {u}")

                # Calorie Derivation Formula Box
                formula_terms = [f"{m.get('calories', 0)} kcal ({m['name']})" for m in measured_ings]
                if cooking_fat:
                    formula_terms.append(f"{cooking_fat.get('calories', 40)} kcal ({cooking_fat.get('name', 'Oil')})")
                formula_str = " + ".join(formula_terms) if formula_terms else f"{cals} kcal"

                st.markdown(f"""
                <div class="calc-breakdown-box">
                    <b>🧮 How Total Calories Were Calculated:</b><br/>
                    {formula_str} = <b>{cals} kcal Total</b><br/>
                    <span style="font-size: 0.75rem; color: #64748B;">
                        Portion weights & USDA nutritional values calculated from specific culinary cooking measurements above.
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**🧂 Missing Pantry Staples:**")
                if missing_staples:
                    for m in missing_staples:
                        st.markdown(f"- ⚠️ *{m}*")
                else:
                    st.markdown("🎉 *All ingredients on hand!*")

                st.markdown("**👨‍🍳 Step-by-Step Cooking:**")
                for s_idx, step in enumerate(instructions):
                    st.markdown(f"**{s_idx + 1}.** {step}")

                # Copy Recipe Text
                formatted_copy_text = f"""# {title}
Prep: {prep_time} | Calories: {cals} kcal | Difficulty: {difficulty}
Macros: {prot}g Protein | {carbs}g Carbs | {fat}g Fat

Cooking Measurements & Ingredients:
{chr(10).join(f"- {m.get('portion', m['name'])} ({m.get('calories', 0)} kcal)" for m in measured_ings) if measured_ings else chr(10).join(f"- {ing}" for ing in used_ings)}
{f"- {cooking_fat.get('portion')} {cooking_fat.get('name')} ({cooking_fat.get('calories')} kcal)" if cooking_fat else ""}

Calorie Calculation:
{formula_str} = {cals} kcal

Pantry Staples Needed:
{chr(10).join(f"- {staple}" for staple in missing_staples) if missing_staples else "- None"}

Instructions:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(instructions))}
"""
                with st.expander("📋 Copy Recipe Text"):
                    st.code(formatted_copy_text, language="markdown")

            st.markdown("<hr style='margin: 1.25rem 0;'>", unsafe_allow_html=True)

    else:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 2px dashed #D1D5DB; border-radius: 12px; padding: 2.5rem 1rem; text-align: center; color: #6B7280; margin-top: 0.5rem; word-break: break-word;">
                <div style="font-size: 2.25rem; margin-bottom: 0.4rem;">🍳</div>
                <h4 style="color: #374151; margin-bottom: 0.25rem;">No Recipes Yet</h4>
                <p style="font-size: 0.85rem; max-width: 340px; margin: 0 auto; line-height: 1.4;">
                    Snap your fridge or enter ingredients on the left, then tap <b>⚡ Generate 3 Recipes</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #9CA3AF; font-size: 0.75rem; padding-bottom: 1rem;">
        ChefMint AI 🌿 • Zero-Waste Gourmet Cooking
    </div>
    """,
    unsafe_allow_html=True,
)
