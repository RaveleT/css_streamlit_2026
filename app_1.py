import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# --- 1. SETTINGS & LUXE DARK THEME ---
st.set_page_config(page_title="Fitness OS 2026", layout="wide", page_icon="⚖️")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #161b22, #0d1117) !important;
        padding: 25px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(3, 166, 161, 0.2) !important;
    }
    [data-testid="stMetricLabel"] p { color: #FFE3BB !important; text-transform: uppercase; font-size: 12px; }
    [data-testid="stMetricValue"] div { color: #03A6A1 !important; font-weight: 300; font-size: 32px; }
    .stMarkdown h2, .stMarkdown h3 { color: #FFE3BB !important; font-weight: 400; margin-top: 2rem !important; }
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid rgba(3, 166, 161, 0.1); }
    hr { border-color: rgba(255, 79, 15, 0.3) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION & FULL DUMMY DATA ---
DUMMY_DATA = [
    {"date": "2025-12-15", "exercises": [{"name": "Barbell Bench Press", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "30"}, {"name": "Push Ups", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": None}, {"name": "Dumbbell Overhead Press", "sets": [{"set": 1, "reps": 1}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "20"}, {"name": "Dynamique Crunch", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": None}, {"name": "Dumbbell Triceps Kickbacks", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "9.5"}, {"name": "Ab Wheel Rollout", "sets": [{"set": 1, "reps": 5}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": None}, {"name": "Kettlebell Goblet Squat", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "10"}, {"name": "Dumbbell Lateral Raise", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}], "weight": "9.5"}, {"name": "Kettlebell Overhead Triceps Extension", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}], "weight": "10"}, {"name": "Rotating Biceps Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "9.5"}]},
    {"date": "2025-12-16", "exercises": [{"name": "Rotating Biceps Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "9.5"}]},
    {"date": "2025-12-22", "exercises": [{"name": "Dynamique Crunch", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": None}, {"name": "Dumbbell Triceps Kickbacks", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "9.5"}, {"name": "Ab Wheel Rollout", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}], "weight": None}, {"name": "Kettlebell Goblet Squat", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}], "weight": "10"}, {"name": "Dumbbell Lateral Raise", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 4, "reps": 12}], "weight": "9.5"}, {"name": "Kettlebell Overhead Triceps Extension", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 4, "reps": 12}], "weight": "10"}, {"name": "Rotating Biceps Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": "9.5"}]},
    {"date": "2025-12-23", "exercises": [{"name": "Kettlebell Goblet Squat", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "10"}, {"name": "Barbell RDL", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 16}, {"set": 3, "reps": 16}], "weight": "30"}, {"name": "Kettlebell Swings", "sets": [{"set": 1, "reps": 20}, {"set": 2, "reps": 20}, {"set": 3, "reps": 20}], "weight": "10"}, {"name": "Bodyweight Lunges", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 17}, {"set": 3, "reps": 18}], "weight": None}, {"name": "Kettlebell Forward Lunges", "sets": [{"set": 1, "reps": 15}, {"set": 2, "reps": 14}, {"set": 3, "reps": 16}], "weight": "10"}, {"name": "Dumbbell Lateral Raise", "sets": [{"set": 1, "reps": 12}, {"set": 2, "reps": 12}, {"set": 3, "reps": 12}, {"set": 4, "reps": 12}], "weight": "9.5"}, {"name": "Cycling", "sets": [{"set": 1, "reps": 70}, {"set": 2, "reps": 75}, {"set": 3, "reps": 80}], "weight": None}, {"name": "Plank", "sets": [{"set": 1, "reps": 60}, {"set": 2, "reps": 60}, {"set": 3, "reps": 60}], "weight": None}]},
    {"date": "2026-01-22", "exercises": [{"name": "Barbell Row", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "30"}, {"name": "Dumbbell Single-Arm Row", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "9.5"}, {"name": "Kettlebell High Pull", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 12}], "weight": "10"}, {"name": "Ab Wheel Rollout", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 12}], "weight": None}, {"name": "Barbell Bicep Curl", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 4}, {"set": 3, "reps": 5}], "weight": "9.5"}, {"name": "Dumbbell Shrug", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 15}, {"set": 3, "reps": 10}], "weight": "9.5"}]},
    {"date": "2026-01-23", "exercises": [{"name": "Barbell Thrusters", "sets": [{"set": 1, "reps": 4}, {"set": 2, "reps": 5}, {"set": 3, "reps": 4}], "weight": "30", "muscle": "Quads / Shoulders"}, {"name": "Dumbbell Step-Ups", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "29.5", "muscle": "Quads / Glutes"}, {"name": "Kettlebell Halos", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "10", "muscle": "Shoulders / Core"}, {"name": "Push Ups", "sets": [{"set": 1, "reps": 16}, {"set": 2, "reps": 16}, {"set": 3, "reps": 7}], "weight": None, "muscle": "Chest / Shoulders"}, {"name": "Dumbbell Squat Jumps", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 15}, {"set": 3, "reps": 15}], "weight": "10", "muscle": "Quads / Calves"}, {"name": "Kettlebell Side Swings", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": None, "muscle": "Core / Shoulders"}, {"name": "Plank", "sets": [{"set": 1, "reps": 60}, {"set": 2, "reps": 60}, {"set": 3, "reps": 60}], "weight": None, "muscle": "Core / Stabilizer"}]}
]

MUSCLE_LOOKUP = {
    "Barbell Bench Press": "Chest", "Push Ups": "Chest / Shoulders", "Push Ups": "Chest / Shoulders",
    "Dumbbell Overhead Press": "Shoulders", "Dynamique Crunch": "Core",
    "Dumbbell Triceps Kickbacks": "Triceps", "Ab Wheel Rollout": "Core",
    "Kettlebell Goblet Squat": "Legs", "Dumbbell Lateral Raise": "Shoulders",
    "Kettlebell Overhead Triceps Extension": "Triceps", "Rotating Biceps Curl": "Biceps",
    "Barbell RDL": "Hamstrings", "Kettlebell Swings": "Full Body",
    "Bodyweight Lunges": "Legs", "Kettlebell Forward Lunges": "Legs",
    "Cycling": "Cardio", "Plank": "Core", "Barbell Row": "Back",
    "Dumbbell Single-Arm Row": "Back", "Kettlebell High Pull": "Shoulders",
    "Barbell Bicep Curl": "Biceps", "Dumbbell Shrug": "Traps",
    "Barbell Thrusters": "Full Body", "Dumbbell Step-Ups": "Legs",
    "Kettlebell Halos": "Shoulders", "Dumbbell Squat Jumps": "Legs",
    "Kettlebell Side Swings": "Core"
}

if 'workout_history' not in st.session_state:
    st.session_state['workout_history'] = DUMMY_DATA

# --- 3. PROCESSING LOGIC ---
def clean_weight(val):
    if val is None or str(val).lower() == 'none': return 0.0
    try: return float(str(val).replace(',', '.'))
    except: return 0.0

def parse_workout_log(log_content):
    lines = log_content.strip().split('\n')
    date_line = next((line for line in lines if line.startswith('Date:')), None)
    date_str = date_line.split(':')[1].strip() if date_line else datetime.now().strftime('%Y-%m-%d')
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
                weight = weight_raw.replace(',', '.').replace('Kg', '').strip() if weight_raw else None
                current_exercise = {'name': name, 'sets': [], 'weight': weight}
    if current_exercise: current_workout['exercises'].append(current_exercise)
    return current_workout

def process_data(json_data):
    records = []
    for session in json_data:
        s_date = pd.to_datetime(session.get('date'))
        for ex in session.get('exercises', []):
            name = ex.get('name')
            muscle_tag = ex.get('muscle') or MUSCLE_LOOKUP.get(name, "Other")
            cats = [c.strip() for c in muscle_tag.split('/')]
            weight = clean_weight(ex.get('weight'))
            for s in ex.get('sets', []):
                records.append({
                    'Date': s_date, 'Day': s_date.strftime('%A'), 'Exercise': name,
                    'Category': cats, 'Weight': weight, 'Reps': s.get('reps', 0),
                    'Volume': weight * s.get('reps', 0)
                })
    return pd.DataFrame(records).explode('Category') if records else pd.DataFrame()

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #03A6A1;'>FITNESS OS</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("System Access", ["Dashboard", "Log Importer", "Progression", "Data Management"])

df = process_data(st.session_state['workout_history'])

# --- 5. DASHBOARD ---
if menu == "Dashboard":
    st.markdown("## Thendo's Fitness Dash")
    if not df.empty:
        unique_sets = df.drop_duplicates(subset=['Date', 'Exercise', 'Weight', 'Reps'])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gross Volume", f"{unique_sets['Volume'].sum():,.0f} kg")
        m2.metric("Sessions", df['Date'].nunique())
        m3.metric("Avg Load", f"{unique_sets[unique_sets['Weight']>0]['Weight'].mean():.1f} kg")
        m4.metric("Last Activity", df['Date'].max().strftime('%d %b'))

        st.divider()
        st.markdown("### 📊 Volume Distribution")
        muscle_vol = df.groupby('Category')['Volume'].sum().reset_index().sort_values('Volume')
        fig1 = px.bar(muscle_vol, x='Volume', y='Category', orientation='h', template="plotly_dark", color_discrete_sequence=['#03A6A1'])
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()
        st.markdown("### 🗓️ Training Consistency")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        consistency = df.drop_duplicates('Date').groupby('Day').size().reindex(day_order, fill_value=0).reset_index(name='Sessions')
        fig2 = px.bar(consistency, x='Day', y='Sessions', template="plotly_dark", color_discrete_sequence=['#FFA673'])
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.markdown("### 🕸️ Muscle Group Balance")
        radar_data = df.groupby('Category')['Volume'].sum().reset_index()
        fig3 = go.Figure(data=go.Scatterpolar(r=radar_data['Volume'], theta=radar_data['Category'], fill='toself', fillcolor='rgba(3, 166, 161, 0.3)', line_color='#03A6A1'))
        fig3.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=False)), height=500)
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()
        st.markdown("### 🏆 Top Exercise Assets")
        top_ex = df.groupby('Exercise').size().reset_index(name='Freq').sort_values('Freq').tail(10)
        fig4 = px.bar(top_ex, x='Freq', y='Exercise', orientation='h', template="plotly_dark", color_discrete_sequence=['#FF4F0F'])
        st.plotly_chart(fig4, use_container_width=True)

# --- 6. LOG IMPORTER ---
elif menu == "Log Importer":
    st.markdown("## 📥 Raw Log Importer")
    st.markdown("Format: `Date: YYYY-MM-DD` then `Exercise(WeightKg)` then `Set->Reps`.")
    raw = st.text_area("Paste text log here:", height=300, placeholder="Date:2026-01-25\nBench Press(50Kg)\n1->10\n2->8")
    if st.button("🚀 Save Workout"):
        if raw:
            new_session = parse_workout_log(raw)
            history = {s['date']: s for s in st.session_state['workout_history']}
            history[new_session['date']] = new_session
            st.session_state['workout_history'] = sorted(list(history.values()), key=lambda x: x['date'])
            st.success("Buffer updated successfully.")
            st.rerun()

# --- 7. PROGRESSION ---
elif menu == "Progression":
    st.markdown("## 📈 Performance Deep-Dive")
    if not df.empty:
        target = st.selectbox("Select Asset", sorted(df['Exercise'].unique()))
        p_data = df[df['Exercise'] == target].groupby('Date').agg({'Weight': 'max', 'Volume': 'sum'}).reset_index()
        fig = px.line(p_data, x='Date', y=['Weight', 'Volume'], markers=True, 
                      template="plotly_dark", color_discrete_sequence=['#03A6A1', '#FF4F0F'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=500)
        st.plotly_chart(fig, use_container_width=True)

# --- 8. DATA MANAGEMENT ---
elif menu == "Data Management":
    st.markdown("## 💾 Data Management")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Purge All Data"):
            st.session_state['workout_history'] = []
            st.rerun()
    with c2:
        if st.button("🔄 Restore Demo Data"):
            st.session_state['workout_history'] = DUMMY_DATA
            st.rerun()
    
    st.divider()
    up = st.file_uploader("Upload History (JSON)", type="json")
    if up:
        st.session_state['workout_history'] = json.load(up)
        st.rerun()
    st.download_button("📤 Export State", data=json.dumps(st.session_state['workout_history'], indent=4), file_name="fitness_os.json")
