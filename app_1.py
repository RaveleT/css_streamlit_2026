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

# Injecting some custom CSS for a cleaner look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div.stButton > button:first-child { background-color: #007bff; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONSTANTS & LOOKUPS ---
null = None # Prevents crash if JSON null is pasted into code area

MUSCLE_LOOKUP = {
    "Barbell Bench Press": "Chest / Triceps", "Push-Ups": "Chest / Shoulders",
    "Dumbbell Overhead Press": "Shoulders", "Dynamique Crunch": "Core",
    "Dumbbell Triceps Kickbacks": "Triceps", "Ab Wheel Rollout": "Core / Abs",
    "Kettlebell Goblet Squat": "Core / Stabilizer", "Dumbbell Lateral Raise": "Shoulders (Lateral)",
    "Kettlebell Overhead Triceps Extension": "Triceps", "Rotating Biceps Curl": "Arms/Biceps",
    "Barbell RDL": "Hamstrings / Back", "Kettlebell Swings": "Full Body",
    "Bodyweight Lunges": "Quads / Glutes", "Kettlebell Forward Lunges": "Quads / Glutes",
    "Cycling": "Hamstrings / Quads", "Plank": "Core / Stabilizer",
    "Barbell Row": "Back / Biceps", "Dumbbell Single-Arm Row-Right": "Back / Biceps",
    "Kettlebell High Pull": "Shoulders / Back", "Barbell Bicep Curl": "Biceps",
    "Dumbbell Shrugs": "Traps", "Barbell Thrusters": "Quads / Shoulders",
    "Dumbbell Step-Ups": "Quads / Glutes", "Kettlebell Halos": "Shoulders / Core",
    "Dumbbell Squat Jumps": "Quads / Calves", "Kettlebell Side Swings": "Core / Shoulders"
}

# --- 3. CORE LOGIC FUNCTIONS ---

def clean_weight(val):
    if val is None: return 0.0
    try:
        clean = re.sub(r'[^0-9.]', '', str(val).replace(',', '.'))
        return float(clean) if clean else 0.0
    except ValueError: return 0.0

def get_muscle_group(ex_name):
    ex_name_clean = ex_name.strip().lower()
    for formal_name, muscle in MUSCLE_LOOKUP.items():
        if ex_name_clean in formal_name.lower(): return muscle
    return "Other"

def parse_workout_log(log_content):
    lines = log_content.strip().split('\n')
    date_line = next((line for line in lines if line.startswith('Date:')), None)
    date_str = date_line.split(':')[1].strip() if date_line else datetime.now().strftime("%Y-%m-%d")
    
    current_workout = {'date': date_str, 'exercises': []}
    current_exercise = None
    SET_REGEX = re.compile(r'(\d+)\s*->\s*(\d+)')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('Date:'): continue
        set_match = SET_REGEX.match(line)
        if set_match:
            if current_exercise:
                current_exercise['sets'].append({'set': int(set_match.group(1)), 'reps': int(set_match.group(2))})
        else:
            if current_exercise: current_workout['exercises'].append(current_exercise)
            name_match = re.match(r'(.+?)(?:\((.+?)\))?$', line)
            if name_match:
                name = name_match.group(1).strip()
                weight_raw = name_match.group(2)
                current_exercise = {
                    'name': name, 'sets': [], 
                    'weight': weight_raw, 
                    'muscle': get_muscle_group(name)
                }
    if current_exercise: current_workout['exercises'].append(current_exercise)
    return current_workout

def process_data(json_data):
    records = []
    for session in json_data:
        s_date = pd.to_datetime(session.get('date'))
        for ex in session.get('exercises', []):
            name = ex.get('name')
            cat = ex.get('muscle', 'Other')
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
    st.session_state['workout_history'] = []

# --- 5. SIDEBAR NAVIGATION ---
st.sidebar.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530c2731ad6f9273d.svg", width=50)
st.sidebar.title("Fitness OS")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Log Importer", "Progression Deep-Dive", "Data Management"])

# --- 6. MENUS ---

# A. DASHBOARD
if menu == "Dashboard":
    st.title("🚀 Training Overview")
    if not st.session_state['workout_history']:
        st.info("No data found. Please go to 'Log Importer' to add your first workout!")
    else:
        df = process_data(st.session_state['workout_history'])
        
        # Top Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Volume", f"{df['Volume'].sum():,.0f} kg")
        c2.metric("Sessions", df['Date'].nunique())
        c3.metric("Avg Intensity", f"{df['Weight'].mean():.1f} kg")
        c4.metric("Last Workout", df['Date'].max().strftime('%b %d'))

        st.divider()
        
        # Volume Heatmap / Distribution
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Volume by Muscle Group")
            fig, ax = plt.subplots()
            df.groupby('Category')['Volume'].sum().sort_values().plot(kind='barh', color='#3498db', ax=ax)
            st.pyplot(fig)
        
        with col_right:
            st.subheader("Training Consistency")
            df['Day'] = df['Date'].dt.date
            daily_vol = df.groupby('Day')['Volume'].sum().reset_index()
            st.line_chart(daily_vol.set_index('Day'))

# B. LOG IMPORTER
elif menu == "Log Importer":
    st.title("📝 Data Entry")
    st.markdown("Paste your workout log below using the standard format.")
    
    col_input, col_help = st.columns([2, 1])
    
    with col_help:
        st.warning("**Required Format:**")
        st.code("Date:2026-01-23\n\nExercise Name(Weight)\n1->Reps\n2->Reps", language="text")
        st.info("If no weight is listed, it defaults to 0 (Bodyweight).")

    with col_input:
        log_text = st.text_area("Raw Workout Log", height=300, placeholder="Date:2026-01-29...")
        if st.button("Save Workout"):
            if "Date:" in log_text:
                parsed_workout = parse_workout_log(log_text)
                # Avoid duplicates: remove old entry for same date
                st.session_state['workout_history'] = [w for w in st.session_state['workout_history'] if w['date'] != parsed_workout['date']]
                st.session_state['workout_history'].append(parsed_workout)
                st.success(f"Successfully saved session for {parsed_workout['date']}")
            else:
                st.error("Log must start with 'Date:YYYY-MM-DD'")

# C. PROGRESSION DEEP-DIVE
elif menu == "Progression Deep-Dive":
    st.title("📈 Detailed Analysis")
    if not st.session_state['workout_history']:
        st.error("Please add data first.")
    else:
        df = process_data(st.session_state['workout_history'])
        df_metrics = df.groupby(['Date', 'Exercise']).agg(
            TotalVolume=('Volume', 'sum'), MaxWeight=('Weight', 'max'), AvgReps=('Reps', 'mean')
        ).reset_index()

        # Selection Logic
        latest_date = df['Date'].max()
        auto_targets = df[df['Date'] == latest_date]['Exercise'].unique().tolist()
        
        target_ex = st.multiselect("Select Exercises to Analyze:", df['Exercise'].unique(), default=auto_targets[:2])

        for exercise in target_ex:
            data = df_metrics[df_metrics['Exercise'] == exercise].sort_values('Date')
            
            with st.container():
                st.subheader(f"Exercise: {exercise}")
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
                
                # Volume & Strength
                sns.lineplot(data=data, x='Date', y='TotalVolume', ax=ax1, marker='o', color='#3498db', label='Volume (kg)')
                ax1_twin = ax1.twinx()
                sns.lineplot(data=data, x='Date', y='MaxWeight', ax=ax1_twin, marker='s', color='#e74c3c', label='Max Weight (kg)')
                ax1.set_ylabel("Volume (kg)", color="#3498db")
                ax1_twin.set_ylabel("Max Weight (kg)", color="#e74c3c")
                
                # Reps
                ax2.bar(data['Date'], data['AvgReps'], color='#2ecc71', alpha=0.5)
                ax2.set_ylabel("Avg Reps")
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
                
                st.pyplot(fig)
                plt.close()

# D. DATA MANAGEMENT
elif menu == "Data Management":
    st.title("💾 Data Export/Import")
    st.write("Manage your persistent workout file.")
    
    # Download
    json_output = json.dumps(st.session_state['workout_history'], indent=4)
    st.download_button("Download workout_data.json", json_output, file_name="workout_data.json", mime="application/json")
    
    st.divider()
    
    # Reset
    if st.button("⚠️ Clear All Local Data"):
        st.session_state['workout_history'] = []
        st.rerun()
