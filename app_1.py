import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import re
from datetime import datetime

# --- 1. SETTINGS & DARK-MODE SAFE STYLING ---
st.set_page_config(page_title="Fitness OS 2026", layout="wide", page_icon="🏋️‍♂️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
    }
    /* Force visibility of text regardless of Light/Dark mode */
    [data-testid="stMetricLabel"] p { color: #555555 !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] div { color: #111111 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE DATA & FALLBACKS ---
null = None
DEFAULT_HISTORY = [
    {"date": "2025-12-15", "exercises": [{"name": "Barbell Bench Press", "sets": [{"set": 1, "reps": 10}, {"set": 2, "reps": 10}, {"set": 3, "reps": 10}], "weight": "30", "muscle": "Chest / Triceps"}]},
    {"date": "2026-01-23", "exercises": [{"name": "Barbell Thrusters", "sets": [{"set": 1, "reps": 4}, {"set": 2, "reps": 5}, {"set": 3, "reps": 4}], "weight": "30", "muscle": "Quads / Shoulders"}, {"name": "Push-Ups", "sets": [{"set": 1, "reps": 16}, {"set": 2, "reps": 16}, {"set": 3, "reps": 7}], "weight": null, "muscle": "Chest / Shoulders"}]}
]

MUSCLE_LOOKUP = {
    "Barbell Bench Press": "Chest / Triceps", "Push-Ups": "Chest / Shoulders",
    "Barbell Thrusters": "Quads / Shoulders", "Barbell RDL": "Hamstrings / Back",
    "Plank": "Core / Stabilizer" # Expand this as needed from your Script 1
}

# --- 3. LOGIC FUNCTIONS ---
def clean_weight(val):
    if val is None or str(val).lower() == 'none': return 0.0
    try:
        return float(str(val).replace(',', '.').replace('Kg', ''))
    except: return 0.0

def process_data_exploded(history):
    rows = []
    for workout in history:
        date = pd.to_datetime(workout.get('date'))
        for ex in workout.get('exercises', []):
            name = ex.get('name')
            # Use saved muscle tag or fallback
            muscle_raw = ex.get('muscle') or MUSCLE_LOOKUP.get(name, "Other")
            categories = [c.strip() for c in muscle_raw.split('/')]
            weight = clean_weight(ex.get('weight'))
            for s in ex.get('sets', []):
                rows.append({
                    'Date': date, 'Exercise': name, 'Categories': categories,
                    'Weight': weight, 'Reps': s.get('reps', 0), 'Volume': weight * s.get('reps', 0)
                })
    df = pd.DataFrame(rows)
    return df.explode('Categories').rename(columns={'Categories': 'Category'}) if not df.empty else df

# --- 4. APP NAVIGATION ---
if 'workout_history' not in st.session_state:
    st.session_state['workout_history'] = DEFAULT_HISTORY

df_exploded = process_data_exploded(st.session_state['workout_history'])

menu = st.sidebar.radio("Navigation", ["Dashboard", "Progression Deep-Dive", "Log Importer", "Raw Data"])

if menu == "Dashboard":
    st.title("🚀 Training Insights")
    
    # 13,336 kg - NOW VISIBLE
    total_vol = df_exploded.drop_duplicates(subset=['Date', 'Exercise', 'Weight', 'Reps'])['Volume'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Volume", f"{total_vol:,.0f} kg")
    c2.metric("Sessions", df_exploded['Date'].nunique())
    c3.metric("Last Entry", df_exploded['Date'].max().strftime('%Y-%m-%d'))

    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Volume by Muscle")
        fig, ax = plt.subplots()
        df_exploded.groupby('Category')['Volume'].sum().sort_values().plot(kind='barh', ax=ax, color='#3498db')
        st.pyplot(fig)
    with col2:
        st.subheader("Muscle Intensity (Heatmap)")
        pivot = df_exploded.pivot_table(index='Category', columns=df_exploded['Date'].dt.strftime('%m-%d'), values='Volume', aggfunc='sum').fillna(0)
        fig, ax = plt.subplots()
        sns.heatmap(pivot, cmap="YlGnBu", annot=True, fmt=".0f", ax=ax)
        st.pyplot(fig)

elif menu == "Progression Deep-Dive":
    st.title("📈 Performance Analysis")
    
    # Auto-Target: Get exercises from the latest session (Script 3 feature)
    latest_date = df_exploded['Date'].max()
    latest_exercises = df_exploded[df_exploded['Date'] == latest_date]['Exercise'].unique()
    
    target = st.selectbox("Select Exercise", options=sorted(df_exploded['Exercise'].unique()), 
                          index=0 if len(latest_exercises) == 0 else list(sorted(df_exploded['Exercise'].unique())).index(latest_exercises[0]))
    
    data = df_exploded[df_exploded['Exercise'] == target].groupby('Date').agg({'Volume': 'sum', 'Weight': 'max', 'Reps': 'mean'}).reset_index()
    
    # Dual Axis Plot (Script 3 feature)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    sns.lineplot(data=data, x='Date', y='Volume', ax=ax1, label='Volume', color='blue', marker='o')
    sns.lineplot(data=data, x='Date', y='Weight', ax=ax2, label='Max Weight', color='red', marker='s')
    ax1.set_ylabel("Volume (kg)", color='blue')
    ax2.set_ylabel("Max Weight (kg)", color='red')
    st.pyplot(fig)

elif menu == "Log Importer":
    st.title("📝 Log New Session")
    raw_log = st.text_area("Paste Log (Date:YYYY-MM-DD followed by exercises)", height=200)
    if st.button("Parse & Save"):
        st.success("Log parsed and added to history!") # Placeholder for your Script 1 parse logic

elif menu == "Raw Data":
    st.write(df_exploded)
