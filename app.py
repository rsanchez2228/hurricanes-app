import streamlit as st
from datetime import datetime
import os
import pandas as pd

# --- Configuration & Theme Setup ---
st.set_page_config(
    page_title="Hialeah Hurricanes 10u Check-In",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED CSS: Forces text inputs and default buttons to stay Blue/Grey and kills the default red outline accent
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    div[data-testid="stSidebar"] { background-color: #1E1E1E; }
    h1, h2, h3 { color: #2196F3 !important; font-family: 'Arial', sans-serif; }
    
    /* Force Text Boxes to have a clean grey look instead of red */
    input {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #2196F3 !important;
    }
    
    /* Standardized player card buttons */
    .stButton>button {
        width: 100%;
        padding: 20px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    /* Pending/Unchecked player styling (Clean dark grey card, no red highlights) */
    div[data-testid="stBaseButton-primary"] {
        background-color: #1E1E1E !important;
        color: #B0BEC5 !important;
        border: 1px solid #424242 !important;
    }
    div[data-testid="stBaseButton-primary"]:hover {
        border-color: #2196F3 !important;
        color: #2196F3 !important;
    }

    /* Checked-in player styling (Bright Blue) */
    div[data-testid="stBaseButton-secondary"] {
        background-color: #2196F3 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

ROSTER_FILE = "roster.txt"
DEFAULT_PLAYERS = [
    "John Doe", "Jane Smith", "Alex Jones", "Mike Miller", 
    "Sam Wilson", "Chris Evans", "Tom Brady", "Patrick Mahomes"
]

# --- Core Persistent Logic ---
def load_roster():
    if not os.path.exists(ROSTER_FILE):
        with open(ROSTER_FILE, "w") as f:
            for player in DEFAULT_PLAYERS:
                f.write(f"{player}\n")
        return sorted(DEFAULT_PLAYERS)
    with open(ROSTER_FILE, "r") as f:
        players = [line.strip() for line in f.readlines() if line.strip()]
    return sorted(players)

def save_roster(players_list):
    with open(ROSTER_FILE, "w") as f:
        for player in players_list:
            f.write(f"{player}\n")

# Initialize Session States
if "players" not in st.session_state:
    st.session_state.players = load_roster()

if "attendance" not in st.session_state:
    st.session_state.attendance = {}

# --- App Header ---
st.title("⚡ Hialeah Hurricanes 10u Team Check-In ⚡")
st.subheader(datetime.now().strftime("%A, %B %d, %Y"))
st.write("---")

# --- 1. ADMIN SIDEBAR ---
with st.sidebar:
    st.header("📋 Admin Controls")
    
    # Add Player Section
    new_name = st.text_input("➕ New Player Name").strip()
    if st.button("Add to Roster", use_container_width=True):
        if new_name and new_name not in st.session_state.players:
            st.session_state.players.append(new_name)
            st.session_state.players.sort()
            save_roster(st.session_state.players)
            st.toast(f" Added {new_name}!", icon="✅")
            st.rerun()
        elif new_name in st.session_state.players:
            st.warning("Player already exists.")

    st.write("---")
    
    # Delete Player Section
    st.write("🗑️ **Manage Roster**")
    player_to_del = st.selectbox("Select player to remove:", [""] + st.session_state.players)
    if st.button("Delete Selected Player", type="primary", use_container_width=True):
        if player_to_del:
            st.session_state.players.remove(player_to_del)
            if player_to_del in st.session_state.attendance:
                del st.session_state.attendance[player_to_del]
            save_roster(st.session_state.players)
            st.toast(f"Removed {player_to_del}", icon="❌")
            st.rerun()

# --- 2. MAIN ATTENDANCE CARD GRID ---
st.write("### Tap Your Name Card To Check In")

# Responsive 3-column grid layout
cols = st.columns(3)
for index, player in enumerate(st.session_state.players):
    col = cols[index % 3]
    
    with col:
        if player in st.session_state.attendance:
            time_str = st.session_state.attendance[player]
            # Checked in button styling
            if st.button(f"🍏 {player}\n({time_str})", key=f"btn_{player}", type="secondary", use_container_width=True):
                del st.session_state.attendance[player]
                st.rerun()
        else:
            # Reconfigured type assignment to sync cleanly with custom dark CSS styles override
            if st.button(player, key=f"btn_{player}", type="primary", use_container_width=True):
                now_time = datetime.now().strftime("%I:%M %p")
                st.session_state.attendance[player] = now_time
                st.rerun()

st.write("---")

# --- 3. EXPORT DATA ---
if st.button("✅ COMPLETED: Download Attendance List", use_container_width=True):
    if not st.session_state.attendance:
        st.error("No data logged yet. Please tap names to check in.")
    else:
        report_data = []
        for player in st.session_state.players:
            status = "Present" if player in st.session_state.attendance else "Absent"
            time_logged = st.session_state.attendance.get(player, "N/A")
            report_data.append([player, status, time_logged])
            
        df = pd.DataFrame(report_data, columns=["Player Name", "Status", "Check-in Time"])
        csv_data = df.to_csv(index=False).encode('utf-8')
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        st.download_button(
            label="💾 Download CSV File to iPad Storage",
            data=csv_data,
            file_name=f"hurricanes_attendance_{today_str}.csv",
            mime="text/csv",
            use_container_width=True
        )
