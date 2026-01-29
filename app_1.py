import streamlit as st
import pandas as pd
import numpy as np
import json
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

null = None

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Researcher Portfolio & Fitness", layout="wide")
warnings.filterwarnings('ignore')
sns.set_theme(style="whitegrid")

# --- 2. DEFAULT FITNESS DATA (Hardcoded so no upload is required) ---
DEFAULT_WORKOUT_JSON = [
    {
        "date": "2025-12-15",
        "exercises": [
            {
                "name": "Barbell Bench Press",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "30"
            },
            {
                "name": "Push Ups",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 15
                    },
                    {
                        "set": 3,
                        "reps": 15
                    }
                ],
                "weight": null
            },
            {
                "name": "Dumbbell Overhead Press",
                "sets": [
                    {
                        "set": 1,
                        "reps": 1
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "20"
            },
            {
                "name": "Dynamique Crunch",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 20
                    },
                    {
                        "set": 3,
                        "reps": 20
                    }
                ],
                "weight": null
            },
            {
                "name": "Dumbbell Triceps Kickbacks",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 15
                    },
                    {
                        "set": 3,
                        "reps": 15
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Ab Wheel Rollout",
                "sets": [
                    {
                        "set": 1,
                        "reps": 5
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": null
            },
            {
                "name": "Kettlebell Goblet Squat",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 15
                    },
                    {
                        "set": 3,
                        "reps": 15
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Dumbbell Lateral Raise",
                "sets": [
                    {
                        "set": 1,
                        "reps": 12
                    },
                    {
                        "set": 2,
                        "reps": 12
                    },
                    {
                        "set": 3,
                        "reps": 12
                    },
                    {
                        "set": 3,
                        "reps": 12
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Kettlebell Overhead Triceps Extension",
                "sets": [
                    {
                        "set": 1,
                        "reps": 12
                    },
                    {
                        "set": 2,
                        "reps": 12
                    },
                    {
                        "set": 3,
                        "reps": 12
                    },
                    {
                        "set": 3,
                        "reps": 12
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Rotating Biceps Curl",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "9.5"
            }
        ]
    },
    {
        "date": "2025-12-16",
        "exercises": [
            {
                "name": "Rotating Biceps Curl",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "9.5"
            }
        ]
    },
    {
        "date": "2025-12-22",
        "exercises": [
            {
                "name": "Dynamique Crunch",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 20
                    },
                    {
                        "set": 3,
                        "reps": 20
                    }
                ],
                "weight": null
            },
            {
                "name": "Dumbbell Triceps Kickbacks",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 15
                    },
                    {
                        "set": 3,
                        "reps": 15
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Ab Wheel Rollout",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    }
                ],
                "weight": null
            },
            {
                "name": "Kettlebell Goblet Squat",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 15
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Dumbbell Lateral Raise",
                "sets": [
                    {
                        "set": 1,
                        "reps": 12
                    },
                    {
                        "set": 2,
                        "reps": 12
                    },
                    {
                        "set": 3,
                        "reps": 12
                    },
                    {
                        "set": 4,
                        "reps": 12
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Kettlebell Overhead Triceps Extension",
                "sets": [
                    {
                        "set": 1,
                        "reps": 12
                    },
                    {
                        "set": 2,
                        "reps": 12
                    },
                    {
                        "set": 3,
                        "reps": 12
                    },
                    {
                        "set": 4,
                        "reps": 12
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Rotating Biceps Curl",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 20
                    },
                    {
                        "set": 3,
                        "reps": 20
                    }
                ],
                "weight": "9.5"
            }
        ]
    },
    {
        "date": "2025-12-23",
        "exercises": [
            {
                "name": "Kettlebell Goblet Squat",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 15
                    },
                    {
                        "set": 3,
                        "reps": 15
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Barbell RDL",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 16
                    },
                    {
                        "set": 3,
                        "reps": 16
                    }
                ],
                "weight": "30"
            },
            {
                "name": "Kettlebell Swings",
                "sets": [
                    {
                        "set": 1,
                        "reps": 20
                    },
                    {
                        "set": 2,
                        "reps": 20
                    },
                    {
                        "set": 3,
                        "reps": 20
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Bodyweight Lunges",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 17
                    },
                    {
                        "set": 3,
                        "reps": 18
                    }
                ],
                "weight": null
            },
            {
                "name": "Kettlebell Forward Lunges",
                "sets": [
                    {
                        "set": 1,
                        "reps": 15
                    },
                    {
                        "set": 2,
                        "reps": 14
                    },
                    {
                        "set": 3,
                        "reps": 16
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Dumbbell Lateral Raise",
                "sets": [
                    {
                        "set": 1,
                        "reps": 12
                    },
                    {
                        "set": 2,
                        "reps": 12
                    },
                    {
                        "set": 3,
                        "reps": 12
                    },
                    {
                        "set": 4,
                        "reps": 12
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Cycling",
                "sets": [
                    {
                        "set": 1,
                        "reps": 70
                    },
                    {
                        "set": 2,
                        "reps": 75
                    },
                    {
                        "set": 3,
                        "reps": 80
                    }
                ],
                "weight": null
            },
            {
                "name": "Plank",
                "sets": [
                    {
                        "set": 1,
                        "reps": 60
                    },
                    {
                        "set": 2,
                        "reps": 60
                    },
                    {
                        "set": 3,
                        "reps": 60
                    }
                ],
                "weight": null
            }
        ]
    },
    {
        "date": "2026-01-22",
        "exercises": [
            {
                "name": "Barbell Row",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "30"
            },
            {
                "name": "Dumbbell  Single-Arm Row-Right",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Dumbbell  Single-Arm Row-Left",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Kettlebell High Pull",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 12
                    }
                ],
                "weight": "10"
            },
            {
                "name": "Ab Wheel Rollout",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 12
                    }
                ],
                "weight": null
            },
            {
                "name": "Barbell Bicep Curl",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 4
                    },
                    {
                        "set": 3,
                        "reps": 5
                    }
                ],
                "weight": "9.5"
            },
            {
                "name": "Dumbbell Shrug",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 15
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "9.5"
            }
        ]
    },
    {
        "date": "2026-01-23",
        "exercises": [
            {
                "name": "Barbell Thrusters",
                "sets": [
                    {
                        "set": 1,
                        "reps": 4
                    },
                    {
                        "set": 2,
                        "reps": 5
                    },
                    {
                        "set": 3,
                        "reps": 4
                    }
                ],
                "weight": "30",
                "muscle": "Quads / Shoulders"
            },
            {
                "name": "Dumbbell Step-Ups",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "29.5",
                "muscle": "Quads / Glutes"
            },
            {
                "name": "Kettlebell Halos",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": "10",
                "muscle": "Shoulders / Core"
            },
            {
                "name": "Push-Ups",
                "sets": [
                    {
                        "set": 1,
                        "reps": 16
                    },
                    {
                        "set": 2,
                        "reps": 16
                    },
                    {
                        "set": 3,
                        "reps": 7
                    }
                ],
                "weight": null,
                "muscle": "Chest / Shoulders"
            },
            {
                "name": "Dumbbell Squat Jumps",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 15
                    },
                    {
                        "set": 3,
                        "reps": 15
                    }
                ],
                "weight": "10",
                "muscle": "Quads / Calves"
            },
            {
                "name": "Kettlebell Side Swings",
                "sets": [
                    {
                        "set": 1,
                        "reps": 10
                    },
                    {
                        "set": 2,
                        "reps": 10
                    },
                    {
                        "set": 3,
                        "reps": 10
                    }
                ],
                "weight": null,
                "muscle": "Core / Shoulders"
            },
            {
                "name": "Plank",
                "sets": [
                    {
                        "set": 1,
                        "reps": 60
                    },
                    {
                        "set": 2,
                        "reps": 60
                    },
                    {
                        "set": 3,
                        "reps": 60
                    }
                ],
                "weight": null,
                "muscle": "Core / Stabilizer"
            }
        ]
    }
]

# --- 3. HELPER FUNCTIONS ---

def categorize_fallback(name):
    name = name.lower()
    mapping = {
        'Chest': ['bench', 'push-up', 'pec'],
        'Back': ['row', 'pull', 'lat', 'shrug'],
        'Shoulders': ['shoulder', 'press', 'lateral'],
        'Legs': ['squat', 'leg', 'lunge', 'deadlift'],
        'Core': ['ab', 'crunch', 'plank']
    }
    for category, keywords in mapping.items():
        if any(word in name for word in keywords): return category
    return 'Other'

def clean_weight_robust(weight_val):
    """Safely converts weight strings/objects to float."""
    if weight_val is None:
        return 0.0
    try:
        # Convert to string and handle European decimal commas
        w_str = str(weight_val).replace(',', '.').strip()
        
        # If it's a range (e.g., "10-12"), take the average or the first number
        if '-' in w_str:
            parts = w_str.split('-')
            return (float(parts[0]) + float(parts[1])) / 2
            
        return float(w_str)
    except (ValueError, TypeError):
        return 0.0

def process_workout_data(raw_data):
    rows = []
    for workout in raw_data:
        date = workout.get('date')
        for ex in workout.get('exercises', []):
            name = ex.get('name')
            cat = ex.get('muscle') if ex.get('muscle') else categorize_fallback(name)
            
            # Use the robust cleaner here to prevent the ValueError
            weight = clean_weight_robust(ex.get('weight'))
            
            for s in ex.get('sets', []):
                reps = s.get('reps', 0)
                rows.append({
                    'Date': pd.to_datetime(date),
                    'Exercise': name,
                    'Category': cat,
                    'Volume': reps * weight,
                    'Weight': weight,
                    'Reps': reps
                })
    return pd.DataFrame(rows)

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["Researcher Profile", "STEM Data Explorer", "Fitness Tracker", "Contact"])

# --- 5. MAIN LOGIC ---

if menu == "Researcher Profile":
    st.title("Researcher Profile")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_1280.jpg", caption="Mr. Thendo Ravele")
    with col2:
        st.write("**Field:** Mathematics & Statistics")
        st.write("**Institution:** University of Venda")
        st.write("**Bio:** Specializing in data science, data-driven mathematical models & data storytelling.")

elif menu == "STEM Data Explorer":
    st.title("STEM Data Explorer")
    st.write("Visualizing Physics and Astronomy experimental data.")
    # (Existing DataFrame code goes here)

elif menu == "Fitness Tracker":
    st.title("🏋️‍♂️ Fitness Analytics & Log Importer")

    # --- 1. THE LOG PARSER (Your Jupyter Logic) ---
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

    def get_muscle_group(ex_name):
        ex_name_clean = ex_name.strip().lower()
        for formal_name, muscle in MUSCLE_LOOKUP.items():
            if ex_name_clean in formal_name.lower(): return muscle
        return "Other"

    def parse_workout_log(log_content):
        lines = log_content.strip().split('\n')
        date_line = next((line for line in lines if line.startswith('Date:')), None)
        date_str = date_line.split(':')[1].strip() if date_line else "N/A"
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
                    current_exercise = {'name': name, 'sets': [], 'weight': weight, 'muscle': get_muscle_group(name)}
        if current_exercise: current_workout['exercises'].append(current_exercise)
        return current_workout

    # --- 2. LOG ENTRY UI ---
    with st.expander("📝 Paste New Workout Log"):
        raw_log = st.text_area("Paste your log here (Format: Date:YYYY-MM-DD followed by exercises)", height=200)
        if st.button("Process Log"):
            if raw_log:
                new_data = parse_workout_log(raw_log)
                # Check if date already exists in DEFAULT_WORKOUT_JSON
                exists = False
                for i, w in enumerate(DEFAULT_WORKOUT_JSON):
                    if w['date'] == new_data['date']:
                        DEFAULT_WORKOUT_JSON[i] = new_data
                        exists = True
                if not exists:
                    DEFAULT_WORKOUT_JSON.append(new_data)
                st.success(f"Added workout for {new_data['date']}!")
            else:
                st.warning("Please paste a log first.")

    # --- 3. ANALYTICS ---
    df = process_workout_data(DEFAULT_WORKOUT_JSON)
    
    # Sidebar Filters
    st.sidebar.subheader("Dashboard Settings")
    selected_year = st.sidebar.selectbox("Year", sorted(df['Date'].dt.year.unique(), reverse=True))
    df_filtered = df[df['Date'].dt.year == selected_year]

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Volume", f"{df_filtered['Volume'].sum():,.0f} kg")
    c2.metric("Sessions", df_filtered['Date'].nunique())
    c3.metric("Top Muscle", df_filtered.groupby('Category')['Volume'].sum().idxmax())

    st.divider()
    
    # Volume Trend Line Chart
    st.subheader("Progress Over Time")
    st.line_chart(df.groupby('Date')['Volume'].sum())

    # Heatmap
    st.subheader("Muscle Group Distribution")
    pivot = df_filtered.pivot_table(index='Category', columns=df_filtered['Date'].dt.strftime('%m-%d'), values='Volume', aggfunc='sum').fillna(0)
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(pivot, cmap="YlGnBu", annot=False, ax=ax)
    st.pyplot(fig)

elif menu == "Contact":
    st.header("Contact")
    st.write("Email: ravele95@gmail.com")
    st.write("Contact No: 060 924 9459")









