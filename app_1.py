import streamlit as st
import pandas as pd
import json
import altair as alt
import re
from datetime import datetime

# --- 1. CONFIGURATION & LOOKUP ---
null = None  # Handle JSON nulls if pasted directly

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

# --- 2. LOGIC FUNCTIONS ---

def get_muscle_group(ex_name):
    ex_name_clean = ex_name.strip().lower()
    for formal_name, muscle in MUSCLE_LOOKUP.items():
        if ex_name_clean in formal_name.lower():
            return muscle
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
                weight = weight_raw.replace(',', '.').lower().replace('kg', '').strip() if weight_raw else None
                current_exercise = {'name': name, 'sets': [], 'weight': weight, 'muscle': get_muscle_group(name)}
    if current_exercise: current_workout['exercises'].append(current_exercise)
    return current_workout

def process_to_dataframe(log_data):
    records = []
    for session in log_data:
        date = pd.to_datetime(session.get('date'))
        for ex in session.get('exercises', []):
            name = ex.get('name')
            cat = ex.get('muscle', 'Other')
            # Robust weight cleaning
            w_raw = ex.get('weight')
            try:
                weight = float(str(w_raw).replace(',', '.')) if w_raw else 0.0
            except: weight = 0.0
            
            for s in ex.get('sets', []):
                reps = s.get('reps', 0)
                records.append({
                    'Date': date, 'Exercise': name, 'Category': cat,
                    'Weight': weight, 'Reps': reps, 'SetVolume': weight * reps
                })
    return pd.DataFrame(records)

# --- 3. STREAMLIT UI ---

st.set_page_config(page_title="Fitness OS", layout="wide")

# Sidebar - App State
if 'data' not in st.session_state:
    st.session_state['data'] = []

st.sidebar.title("Settings")
uploaded_file = st.sidebar.file_uploader("Upload existing JSON", type=['json'])
if uploaded_file:
    st.session_state['data'] = json.load(uploaded_file)

# --- TAB 1: LOG IMPORTER ---
tab1, tab2 = st.tabs(["📝 Log Importer", "📈 Analytics"])

with tab1:
    st.subheader("Import Workout from Text")
    
    col_in, col_pre = st.columns([1, 1])
    
    with col_in:
        example_format = "Date:2026-01-23\n\nBarbell Thrusters(30kg)\n1->5\n2->5\n\nPush-Ups\n1->20"
        raw_log = st.text_area("Paste Raw Log Here:", value=example_format, height=300)
        if st.button("Add to Database"):
            parsed = parse_workout_log(raw_log)
            # Remove existing entry for same date to prevent duplicates
            st.session_state['data'] = [w for w in st.session_state['data'] if w['date'] != parsed['date']]
            st.session_state['data'].append(parsed)
            st.success(f"Successfully processed workout for {parsed['date']}!")

    with col_pre:
        st.info("**Format Instructions:**\n1. Start with `Date:YYYY-MM-DD`\n2. Exercise Name (Optional Weight in Brackets)\n3. SetNumber -> Reps")
        st.json(st.session_state['data'][-1] if st.session_state['data'] else {})

# --- TAB 2: ANALYTICS ---
with tab2:
    if not st.session_state['data']:
        st.warning("No data found. Upload a JSON or paste a log in the Importer tab.")
    else:
        df = process_to_dataframe(st.session_state['data'])
        
        # Selectors
        exercises = sorted(df['Exercise'].unique())
        target_ex = st.selectbox("Select Exercise for Progression:", exercises, index=exercises.index('Barbell RDL') if 'Barbell RDL' in exercises else 0)

        # CHART 1: Muscle Distribution
        st.subheader("Muscle Group Volume")
        muscle_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('sum(SetVolume):Q', title='Total Volume (kg)'),
            y=alt.Y('Category:N', sort='-x'),
            color='Category:N',
            tooltip=['Category', 'sum(SetVolume)']
        ).properties(height=300)
        st.altair_chart(muscle_chart, use_container_width=True)

        # CHART 2: Exercise Progression
        st.subheader(f"Progression: {target_ex}")
        prog_data = df[df['Exercise'] == target_ex].groupby('Date')['SetVolume'].sum().reset_index()
        
        prog_chart = alt.Chart(prog_data).mark_line(point=True).encode(
            x='Date:T',
            y=alt.Y('SetVolume:Q', title='Daily Volume (kg)'),
            tooltip=['Date', 'SetVolume']
        ).properties(height=300)
        st.altair_chart(prog_chart, use_container_width=True)
        
        # Download data
        st.sidebar.divider()
        json_string = json.dumps(st.session_state['data'], indent=4)
        st.sidebar.download_button(
            label="Download Data as JSON",
            data=json_string,
            file_name="workout_data.json",
            mime="application/json"
        )
