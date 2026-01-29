import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import re
from datetime import datetime

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Fitness OS 2026", layout="wide", page_icon="🏋️‍♂️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div.stButton > button:first-child { background-color: #007bff; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONSTANTS & DEFAULT DATA ---
null = None 

# The data you provided
DEFAULT_HISTORY = [
    {"date": "2025-12-15", "exercises": [{"name": "Barbell Bench Press", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "30"}, {"name": "Push Ups", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": null}, {"name": "Dumbbell Overhead Press", "sets": [{"set": 1, "reps": 1}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "20"}, {"name": "Dynamique Crunch", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": null}, {"name": "Dumbbell Triceps Kickbacks", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "9.5"}, {"name": "Ab Wheel Rollout", "sets": [{"set": 1, "reps": 5}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": null}, {"name": "Kettlebell Goblet Squat", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "10"}, {"name": "Dumbbell Lateral Raise", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 3, "reps": 12}], "weight": "9.5"}, {"name": "Kettlebell Overhead Triceps Extension", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 3, "reps": 12}], "weight": "10"}, {"name": "Rotating Biceps Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "9.5"}]},
    {"date": "2025-12-16", "exercises": [{"name": "Rotating Biceps Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "9.5"}]},
    {"date": "2025-12-22", "exercises": [{"name": "Dynamique Crunch", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": null}, {"name": "Dumbbell Triceps Kickbacks", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "9.5"}, {"name": "Ab Wheel Rollout", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}], "weight": null}, {"name": "Kettlebell Goblet Squat", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}], "weight": "10"}, {"name": "Dumbbell Lateral Raise", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 4, "reps": 12}], "weight": "9.5"}, {"name": "Kettlebell Overhead Triceps Extension", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 4, "reps": 12}], "weight": "10"}, {"name": "Rotating Biceps Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": "9.5"}]},
    {"date": "2025-12-23", "exercises": [{"name": "Kettlebell Goblet Squat", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "10"}, {"name": "Barbell RDL", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 16}, {"set": 3, "reps": 16}], "weight": "30"}, {"name": "Kettlebell Swings", "sets": [{"set": 1, "reps": 20}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": "10"}, {"name": "Bodyweight Lunges", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 17}, {"set": 3, "reps": 18}], "weight": null}, {"name": "Kettlebell Forward Lunges", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 14}, {"set": 3, "reps": 16}], "weight": "10"}, {"name": "Dumbbell Lateral Raise", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 4, "reps": 12}], "weight": "9.5"}, {"name": "Cycling", "sets": [{"set": 1, "reps": 70}, {"set": 2, "reps": 75}, {"set": 3, "reps": 80}], "weight": null}, {"name": "Plank", "sets": [{"set": 1, "reps": 60}, {"set": 2, "reps": 60}, {"set": 3, "reps": 60}], "weight": null}]},
    {"date": "2026-01-22", "exercises": [{"name": "Barbell Row", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "30"}, {"name": "Dumbbell Single-Arm Row-Right", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "9.5"}, {"name": "Dumbbell Single-Arm Row-Left", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "9.5"}, {"name": "Kettlebell High Pull", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 12}], "weight": "10"}, {"name": "Ab Wheel Rollout", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 12}], "weight": null}, {"name": "Barbell Bicep Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 4}, {"set": 3, "reps": 5}], "weight": "9.5"}, {"name": "Dumbbell Shrug", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 15}, {"set": 3, "reps": 10}], "weight": "9.5"}]},
    {"date": "2026-01-23", "exercises": [{"name": "Barbell Thrusters", "sets": [{"set": 1, "reps": 4}, {"set": 2, "reps": 5}, {"set": 3, "reps": 4}], "weight": "30"}, {"name": "Dumbbell Step-Ups", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "29.5"}, {"name": "Kettlebell Halos", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "10"}, {"name": "Push-Ups", "sets": [{"set": 1, "reps": 16}, {"set": 2, "reps": 16}, {"set": 3, "reps": 7}], "weight": null}, {"name": "Dumbbell Squat Jumps", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "10"}, {"name": "Kettlebell Side Swings", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": null}, {"name": "Plank", "sets": [{"set": 1, "reps": 60}, {"set": 2, "reps": 60}, {"set": 3, "reps": 60}], "weight": null}]}
]

MUSCLE_LOOKUP = {
    "Barbell Bench Press": "Chest", "Push-Ups": "Chest / Shoulders", "Push Ups": "Chest / Shoulders",
    "Dumbbell Overhead Press": "Shoulders", "Dynamique Crunch": "Core",
    "Dumbbell Triceps Kickbacks": "Triceps", "Ab Wheel Rollout": "Core",
    "Kettlebell Goblet Squat": "Legs", "Dumbbell Lateral Raise": "Shoulders",
    "Kettlebell Overhead Triceps Extension": "Triceps", "Rotating Biceps Curl": "Biceps",
    "Barbell RDL": "Hamstrings", "Kettlebell Swings": "Full Body",
    "Bodyweight Lunges": "Legs", "Kettlebell Forward Lunges": "Legs",
    "Cycling": "Cardio", "Plank": "Core", "Barbell Row": "Back",
    "Single-Arm Row": "Back", "Kettlebell High Pull": "Shoulders",
    "Barbell Bicep Curl": "Biceps", "Dumbbell Shrug": "Traps",
    "Barbell Thrusters": "Full Body", "Dumbbell Step-Ups": "Legs",
    "Kettlebell Halos": "Shoulders", "Dumbbell Squat Jumps": "Legs",
    "Kettlebell Side Swings": "Core"
}

# --- 3. CORE LOGIC ---
def clean_weight(val):
    if val is None or str(val).lower() == 'none': return 0.0
    try:
        clean = re.sub(r'[^0-9.]', '', str(val).replace(',', '.'))
        return float(clean) if clean else 0.0
    except ValueError: return 0.0

def get_muscle_group(ex_name):
    ex_name_clean = ex_name.strip().lower()
    for formal_name, muscle in MUSCLE_LOOKUP.items():
        if formal_name.lower() in ex_name_clean: return muscle
    return "Other"

def process_data(json_data):
    records = []
    for session in json_data:
        s_date = pd.to_datetime(session.get('date'))
        for ex in session.get('exercises', []):
            name = ex.get('name')
            cat = get_muscle_group(name)
            weight = clean_weight(ex.get('weight'))
            for s in ex.get('sets', []):
                reps = s.get('reps', 0)
                records.append({
                    'Date': s_date, 'Exercise': name, 'Category': cat,
                    'Weight': weight, 'Reps': reps, 'Volume': weight * reps
                })
    return pd.DataFrame(records)

# --- 4. SESSION STATE ---
if 'workout_history' not in st.session_state:
    st.session_state['workout_history'] = DEFAULT_HISTORY

# --- 5. UI ---
st.sidebar.title("🏋️‍♂️ Fitness OS")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Log Importer", "Progression Deep-Dive", "Data Management"])

if menu == "Dashboard":
    st.title("🚀 Training Overview")
    df = process_data(st.session_state['workout_history'])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Volume", f"{df['Volume'].sum():,.0f} kg")
    c2.metric("Total Sessions", df['Date'].nunique())
    c3.metric("Avg Weight", f"{df[df['Weight']>0]['Weight'].mean():.1f} kg")
    c4.metric("Last Workout", df['Date'].max().strftime('%b %d'))

    st.divider()
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Volume by Muscle Group")
        fig, ax = plt.subplots()
        df.groupby('Category')['Volume'].sum().sort_values().plot(kind='barh', color='#3498db', ax=ax)
        st.pyplot(fig)
    
    with col_right:
        st.subheader("Training Consistency")
        daily_vol = df.groupby(df['Date'].dt.date)['Volume'].sum().reset_index()
        st.line_chart(daily_vol.set_index('Date'))

elif menu == "Progression Deep-Dive":
    st.title("📈 Exercise Analysis")
    df = process_data(st.session_state['workout_history'])
    target_ex = st.selectbox("Select Exercise:", sorted(df['Exercise'].unique()))
    
    data = df[df['Exercise'] == target_ex].groupby('Date').agg({'Weight': 'max', 'Volume': 'sum'}).reset_index()
    st.line_chart(data.set_index('Date')[['Weight', 'Volume']])

elif menu == "Data Management":
    st.title("💾 Data Export")
    json_output = json.dumps(st.session_state['workout_history'], indent=4)
    st.download_button("Download workout_data.json", json_output, file_name="workout_data.json")
    if st.button("Clear History"):
        st.session_state['workout_history'] = []
        st.rerun()
