import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# --- 0. Page Configuration & UI Cleanup ---
st.set_page_config(layout="wide", page_title="Digital Twin")

# Custom CSS to hide the GitHub icon, Deploy button, and footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display:none !important;}
            div[data-testid="stToolbar"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

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
    
    /* Profile Specific Styling */
    .skill-tag {
        background-color: #161b22;
        border: 1px solid #03A6A1;
        color: #03A6A1;
        padding: 8px 16px;
        border-radius: 20px;
        margin-right: 8px;
        display: inline-block;
        margin-bottom: 10px;
        font-size: 14px;
        transition: 0.3s;
    }
    .skill-tag:hover {
        background-color: #03A6A1;
        color: #0E1117;
    }
    .contact-link {
        color: #03A6A1 !important;
        text-decoration: none;
        margin: 0 10px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADING FROM SECRETS ---
@st.cache_data
def load_initial_data():
    if "workout_data" in st.secrets:
        raw_json = st.secrets["workout_data"].strip()
        raw_json = raw_json.replace(": None", ": null").replace(":None", ":null")
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON Syntax Error: {e.msg}")
            return []
    return []

MUSCLE_LOOKUP = {
    "Barbell Bench Press": "Chest", "Push Ups": "Chest / Shoulders",
    "Dumbbell Overhead Press": "Shoulders", "Dynamique Crunch": "Core",
    "Dumbbell Triceps Kickbacks": "Triceps", "Ab Wheel Rollout": "Core",
    "Kettlebell Goblet Squat": "Legs", "Dumbbell Lateral Raise": "Shoulders",
    "Kettlebell Overhead Triceps Extension": "Triceps", "Rotating Biceps Curl": "Biceps",
    "Barbell RDL": "Hamstrings", "Kettlebell Swings": "Full Body",
    "Cycling": "Cardio", "Plank": "Core", "Barbell Row": "Back",
    "Dumbbell Single-Arm Row-Right": "Back", "Dumbbell Single-Arm Row-Left": "Back",
    "Barbell Bicep Curl": "Biceps", "Barbell Thrusters": "Full Body"
}

if 'workout_history' not in st.session_state:
    st.session_state['workout_history'] = load_initial_data()

# --- 3. LOGIC FUNCTIONS ---
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
                reps = s.get('reps', 0)
                vol = reps if (name == "Cycling" or "Cardio" in cats) else (weight * reps)
                records.append({
                    'Date': s_date, 'Day': s_date.strftime('%A'), 'Exercise': name,
                    'Category': cats, 'Weight': weight, 'Reps': reps, 'Volume': vol
                })
    return pd.DataFrame(records).explode('Category') if records else pd.DataFrame()

# --- 4. DATA INITIALIZATION & SIDEBAR ---
full_df = process_data(st.session_state['workout_history'])

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #03A6A1;'>FITNESS OS</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("System Access", ["Profile", "Dashboard", "Log Importer", "Progression", "Data Management"])
    
    st.divider()
    if not full_df.empty and menu != "Profile":
        min_date = full_df['Date'].min().to_pydatetime()
        max_date = full_df['Date'].max().to_pydatetime()
        selected_range = st.slider("Select Training Period", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="DD/MM/YY")
        df = full_df[(full_df['Date'] >= selected_range[0]) & (full_df['Date'] <= selected_range[1])]
    else:
        df = full_df

# --- 5. PROFILE PAGE ---
if menu == "Profile":
    st.markdown("## 👤 User Profile")
    
    # Hero Identity Section
    st.markdown(f"""
        <div style="padding: 40px; background: linear-gradient(145deg, #161b22, #0d1117); 
                    border-radius: 20px; border: 1px solid rgba(3, 166, 161, 0.2); 
                    text-align: center; margin-bottom: 30px;">
            <h1 style="margin: 0; color: #03A6A1; font-weight: 300; letter-spacing: 2px;">THENDO RAVELE</h1>
            <p style="color: #FFE3BB; font-size: 1.3rem; margin-top: 10px; font-weight: 400;">Math & Statistics Scholar</p>
            <p style="font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px;">University of Venda (Univen)</p>
            <div style="margin-top: 20px; border-top: 1px solid rgba(255, 227, 187, 0.1); padding-top: 20px;">
                <a href="mailto:ravele95@gmail.com" class="contact-link">📧 ravele95@gmail.com</a>
                <span style="color: #444;">|</span>
                <a href="tel:0609249459" class="contact-link">📱 060 924 9459</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Core Competencies (Metrics)
    st.markdown("### 📈 Analytical Focus")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Modeling", "ODEs / LiDAR")
    with m_col2:
        st.metric("Statistics", "Linear Reg / EDA")
    with m_col3:
        st.metric("Engineering", "ETL Pipelines")
    
    st.divider()

    # Technical Stack
    st.markdown("### 🛠️ Programming & Tools")
    skills = ["Python", "R", "MATLAB", "Java", "C++", "Javascript", "Bash", "Jupyter Notebook", "Mathematical Modelling"]
    skill_html = "".join([f'<span class="skill-tag">{s}</span>' for s in skills])
    st.markdown(f'<div style="margin-bottom: 30px;">{skill_html}</div>', unsafe_allow_html=True)

    # Data Science Workflow
    st.markdown("### 🧬 Data Engineering & Analysis")
    st.markdown("""
        <div style="background-color: rgba(3, 166, 161, 0.05); border-left: 4px solid #03A6A1; 
                    padding: 25px; border-radius: 12px; margin-bottom: 30px;">
            <p style="margin: 0; color: #FFE3BB; line-height: 1.6; font-size: 1.1rem;">
                Expertise in the full data lifecycle: <b>ETL</b> (Extract, Transform, Load) processes for data integration, 
                and <b>EDA</b> (Exploratory Data Analysis) to uncover patterns. Proficient in using <b>Jupyter Notebooks</b> 
                for reproducible research and collaborative development.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    

    # LiDAR & Digital Twins
    st.markdown("### 🛰️ Spatial Data & Digital Twins")
    st.markdown("""
        <div style="background-color: rgba(255, 79, 15, 0.05); border-left: 4px solid #FF4F0F; 
                    padding: 25px; border-radius: 12px; margin-bottom: 30px;">
            <h4 style="color: #FF4F0F; margin-top: 0;">Point Cloud Engineering</h4>
            <p style="margin: 0; color: #FFE3BB; font-size: 1.1rem; line-height: 1.6;">
                Specialized in high-density <b>LiDAR data</b> and <b>Photogrammetry</b>. 
                Focusing on building <b>Digital Twins</b> through rigorous <b>point cloud data</b> 
                cleaning and processing for spatial accuracy.
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- 6. DASHBOARD ---
elif menu == "Dashboard":
    st.markdown("## Thendo's Fitness Dash")
    if not df.empty:
        unique_sets = df.drop_duplicates(subset=['Date', 'Exercise', 'Weight', 'Reps'])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gross Volume", f"{unique_sets['Volume'].sum():,.0f} pts")
        m2.metric("Sessions", df['Date'].nunique())
        m3.metric("Avg Load", f"{unique_sets[unique_sets['Weight']>0]['Weight'].mean():.1f} kg")
        m4.metric("Last Activity", df['Date'].max().strftime('%d %b'))

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Volume Distribution")
            muscle_vol = df.groupby('Category')['Volume'].sum().reset_index().sort_values('Volume')
            st.plotly_chart(px.bar(muscle_vol, x='Volume', y='Category', orientation='h', template="plotly_dark", color_discrete_sequence=['#03A6A1']), use_container_width=True)
        
        with col2:
            st.markdown("### 🕸️ Muscle Balance")
            radar_data = df.groupby('Category')['Volume'].sum().reset_index()
            fig_radar = go.Figure(data=go.Scatterpolar(r=radar_data['Volume'], theta=radar_data['Category'], fill='toself', fillcolor='rgba(3, 166, 161, 0.3)', line_color='#03A6A1'))
            fig_radar.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=False)), height=400)
            st.plotly_chart(fig_radar, use_container_width=True)

        st.divider()
        st.markdown("### 🗓️ Training Consistency")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        consistency = df.drop_duplicates('Date').groupby('Day').size().reindex(day_order, fill_value=0).reset_index(name='Sessions')
        st.plotly_chart(px.bar(consistency, x='Day', y='Sessions', template="plotly_dark", color_discrete_sequence=['#FF4F0F']), use_container_width=True)

        st.divider()
        st.markdown("### 🏆 Top Exercise Assets")
        top_ex = df.groupby('Exercise').size().reset_index(name='Freq').sort_values('Freq').tail(10)
        st.plotly_chart(px.bar(top_ex, x='Freq', y='Exercise', orientation='h', template="plotly_dark", color_discrete_sequence=['#03A6A1']), use_container_width=True)

# --- 7. LOG IMPORTER ---
elif menu == "Log Importer":
    st.markdown("## 📥 Raw Log Importer")
    raw = st.text_area("Paste text log here:", height=300, placeholder="Date:2026-01-25\nBench Press(50Kg)\n1->10\n2->8")
    if st.button("🚀 Save Workout"):
        if raw:
            new_session = parse_workout_log(raw)
            history = {s['date']: s for s in st.session_state['workout_history']}
            history[new_session['date']] = new_session
            st.session_state['workout_history'] = sorted(list(history.values()), key=lambda x: x['date'])
            st.success("Buffer updated successfully.")
            st.rerun()

# --- 8. PROGRESSION ---
elif menu == "Progression":
    st.markdown("## 📈 Performance Deep-Dive")
    if not df.empty:
        exercise_list = sorted(df['Exercise'].unique())
        try:
            default_index = list(exercise_list).index("Cycling")
        except ValueError:
            default_index = 0
            
        target = st.selectbox("Select Asset", exercise_list, index=default_index)
        p_data = df[df['Exercise'] == target].groupby('Date').agg({'Weight': 'max', 'Volume': 'sum'}).reset_index()
        fig = px.line(p_data, x='Date', y=['Weight', 'Volume'], markers=True, 
                      template="plotly_dark", color_discrete_sequence=['#03A6A1', '#FF4F0F'])
        st.plotly_chart(fig, use_container_width=True)

# --- 9. DATA MANAGEMENT ---
elif menu == "Data Management":
    st.markdown("## 💾 Data Management")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Purge All Data"):
            st.session_state['workout_history'] = []
            st.rerun()
    with c2:
        if st.button("🔄 Reload Demo Data"):
            st.session_state['workout_history'] = load_initial_data()
            st.rerun()
    
    st.divider()
    up = st.file_uploader("Upload History (JSON)", type="json")
    if up:
        st.session_state['workout_history'] = json.load(up)
        st.rerun()
    st.download_button("📤 Export State", data=json.dumps(st.session_state['workout_history'], indent=4), file_name="fitness_os.json")



