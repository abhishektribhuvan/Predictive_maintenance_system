import streamlit as st
import random
import time
import requests
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Anomaly Detection System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Dark'

# State to hold multiple machines in our distributed system
if 'machines' not in st.session_state:
    st.session_state.machines = {
        "Default-MAC-1111": {"name": "Test Machine Alpha"}
    }

if 'selected_machine' not in st.session_state:
    st.session_state.selected_machine = None

# Custom CSS for Theme switching & Premium UI
def apply_theme():
    if st.session_state.theme == 'Dark':
        css = """
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        /* Dashboard Cards */
        .machine-card {
            background-color: #1E2129;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.4);
            border: 1px solid #2A2D35;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .machine-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 255, 128, 0.15);
            border-color: #00FF80;
        }
        /* Metrics styling */
        div[data-testid="metric-container"] {
            background-color: #262730;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        }
        /* Indicators */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background-color: #00FF80; box-shadow: 0 0 8px #00FF80; align-items: center;}
        .status-inactive { background-color: #FF3333; box-shadow: 0 0 8px #FF3333; }
        </style>
        """
    else:
        css = """
        <style>
        .stApp {
            background-color: #F8F9FA;
            color: #111827;
        }
        /* Dashboard Cards */
        .machine-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #E5E7EB;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .machine-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            border-color: #6366F1;
        }
        div[data-testid="metric-container"] {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            border: 1px solid #E5E7EB;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background-color: #10B981; }
        .status-inactive { background-color: #EF4444; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

apply_theme()

# --- Sidebar Navigation ---
st.sidebar.title("Distributed System")

# If we are viewing a specific machine, give an option to go back
if st.session_state.selected_machine:
    if st.sidebar.button("🔙 Back to All Machines"):
        st.session_state.selected_machine = None
        st.rerun()

menu = ["Machine Status", "Add New Machine", "Settings"]
# Keep choice managed but if we are on selected_machine, we override the view
choice = st.sidebar.radio("Navigation", menu)

if st.session_state.selected_machine:
    st.sidebar.info(f"Currently viewing: {st.session_state.machines[st.session_state.selected_machine]['name']}")


# -------------------------------------------------------------------------
# View 0: Specific Machine Details
# -------------------------------------------------------------------------
if st.session_state.selected_machine:
    mac_id = st.session_state.selected_machine
    machine_info = st.session_state.machines[mac_id]
    
    st.title(f"🔍 Machine Details: {machine_info['name']}")
    st.caption(f"**MAC ID / Device ID:** {mac_id}")
    
    st.markdown("---")
    res_col1, res_col2 = st.columns([3, 1])
    
    with res_col1:
        st.subheader("Current Metrics & Health")
        
        # -------------------------------------------------------------
        # API REQUIREMENT: Prediction Data
        # Endpoint: GET /predict_latest/{device_id}
        # Returns the latest anomaly prediction from the trained model.
        # -------------------------------------------------------------
        def fetch_machine_data(device_id):
            try:
                # Assuming the backend is running locally for demonstration
                response = requests.get(f"http://127.0.0.1:8000/predict_latest/{device_id}", timeout=2)
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
            except:
                return None

        if st.button("🔄 Refresh Data", key="refresh_detail"):
            st.rerun()

        data = fetch_machine_data(mac_id)

        if data:
            if data.get("status") == "Normal":
                st.success("✅ Machine Health: **NORMAL**")
            else:
                st.error("🚨 Machine Health: **ANOMALY DETECTED**")
            
            col_mean, col_var, col_temp = st.columns(3)
            with col_mean:
                st.metric(label="Mean", value=f"{data['mean']:.2f}")
                st.progress(int(max(0, min(100, data["mean"]))))
            with col_var:
                st.metric(label="Variance", value=f"{data['var']:.2f}")
                st.progress(int(max(0, min(100, data["var"]))))
            with col_temp:
                st.metric(label="Temperature (°C)", value=f"{data['temp']:.2f}")
                st.progress(int(max(0, min(100, data["temp"]/2)))) # Scaled roughly for progress bar
        else:
            st.warning(f"No prediction data found for {mac_id}. Have you sent data and trained the model?")

    with res_col2:
        st.subheader("Configuration")
        st.button("⚙️ Device Settings", use_container_width=True)
        
        if st.button("🧠 Retrain Model", use_container_width=True, type="primary"):
            # -------------------------------------------------------------
            # API REQUIREMENT: Model Training
            # Endpoint: GET /train/{device_id}
            # Tells backend to train IsolationForest on {device_id}_training_data.csv
            # -------------------------------------------------------------
            with st.spinner("Training model using device data..."):
                try:
                    res = requests.get(f"http://127.0.0.1:8000/train/{mac_id}", timeout=5)
                    if res.status_code == 200:
                        st.success("Model trained successfully!")
                    else:
                        st.error(f"Error: {res.json().get('detail', 'Not enough data')}")
                except Exception as e:
                    st.error(f"Backend unreachable: {e}")

        if st.button("📈 View Historical Data", use_container_width=True):
            st.info("Fetching old data...")
            # -------------------------------------------------------------
            # API REQUIREMENT: Historical Data Retrieval 
            # Needs an endpoint like `GET /history/{mac_id}` returning a list of past metrics.
            # -------------------------------------------------------------
            try:
                # We can manually read the CSV directly if on same machine for demonstration
                csv_path = f"{mac_id}_training_data.csv"
                df = pd.read_csv(csv_path)
                st.dataframe(df.tail(10)) 
            except FileNotFoundError:
                st.error("No historical data file found for this device.")


# -------------------------------------------------------------------------
# View 1: Machine Status Dashboard
# -------------------------------------------------------------------------
elif choice == "Machine Status":
    st.title("🌐 Multi-Machine Status Dashboard")
    st.markdown("Monitor all distributed systems in one centralized view.")
    
    # Grid Layout with Search
    col_search, col_space = st.columns([2, 2])
    with col_search:
        search_query = st.text_input("🔍 Search by Machine ID or Name", "")

    st.markdown("---")
    
    if len(st.session_state.machines) == 0:
        st.info("No machines configured. Go to 'Add New Machine' to add one.")
    else:
        # Filter machines
        filtered_macs = [mac for mac, info in st.session_state.machines.items() 
                         if search_query.lower() in mac.lower() or search_query.lower() in info["name"].lower()]
        
        if not filtered_macs:
            st.warning("No machines match your search.")
        else:
            # Create a nice 3-column UI grid
            cols = st.columns(3)
            
            for index, mac_id in enumerate(filtered_macs):
                machine_info = st.session_state.machines[mac_id]
                col = cols[index % 3]
                
                with col:
                    # -------------------------------------------------------------
                    # API REQUIREMENT: Live Connection/Active Status
                    # We need an endpoint (e.g., `GET /device_status/{mac_id}`) or a WebSocket connection
                    # to indicate if the ESP32 is actively sending data.
                    # For now, this is randomized as requested.
                    # -------------------------------------------------------------
                    is_active = random.choice([True, False])
                    
                    status_class = "status-active" if is_active else "status-inactive"
                    status_text = "Receiving Data" if is_active else "Inactive"
                    
                    # Custom Card HTML/CSS implementation snippet wrapped in markdown
                    st.markdown(f"""
                    <div class="machine-card">
                        <h4 style="margin-top:0;">{machine_info['name']}</h4>
                        <p style="color: gray; font-size: 0.9em; margin-bottom: 10px;">ID: {mac_id}</p>
                        <div>
                            <span class="status-indicator {status_class}"></span>
                            <span style="font-size: 0.85em; font-weight: bold;">{status_text}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Manage Button specifically for this machine
                    if st.button("Manage & Details", key=f"btn_{mac_id}", use_container_width=True):
                        st.session_state.selected_machine = mac_id
                        st.rerun()

# -------------------------------------------------------------------------
# View 2: Add New Machine Configuration
# -------------------------------------------------------------------------
elif choice == "Add New Machine":
    st.title("⚙️ Add New Distributed Device")

    st.markdown("### Device Configuration")
    
    with st.form("create_machine_form", clear_on_submit=True):
        mac_id_input = st.text_input("Device MAC ID / Unique ID", placeholder="e.g. MAC-102030")
        custom_name_input = st.text_input("Custom Machine Name", placeholder="e.g. Compressor Unit 2")
        
        submit_machine = st.form_submit_button("➕ Add Device")
        
        if submit_machine:
            if not mac_id_input or not custom_name_input:
                st.error("Both MAC ID and Custom Name are required!")
            elif mac_id_input in st.session_state.machines:
                st.error("A machine with this MAC ID already exists.")
            else:
                # Add to state immediately
                st.session_state.machines[mac_id_input] = {
                    "name": custom_name_input
                }
                # -------------------------------------------------------------
                # API REQUIREMENT: Device Registry
                # You might need a `POST /register_device` endpoint to save this permanently 
                # on a backend database, otherwise it disappears on app restart.
                # -------------------------------------------------------------
                st.success(f"Device '{custom_name_input}' ({mac_id_input}) added successfully!")
                st.balloons()

# -------------------------------------------------------------------------
# View 3: Settings
# -------------------------------------------------------------------------
elif choice == "Settings":
    st.title("🎛️ Settings")

    st.markdown("### Appearance")
    new_theme = st.radio("Select Theme:", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1)
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.divider()

    st.markdown("### System Log")
    if st.button("🚪 Logout", type="primary"):
        st.success("Logged out successfully.")
