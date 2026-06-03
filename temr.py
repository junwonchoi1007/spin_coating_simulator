import streamlit as st
import numpy as np
import pandas as pd

# 1. Page Layout and App Title
st.set_page_config(layout="wide")
st.title("🎯 Spin Coating Process Simulator & Validation")

# 2. Sidebar Sliders (Design-Exploration Mode)
st.sidebar.header("🔧 Process Parameters")
omega_rpm = st.sidebar.slider("Rotational Speed (RPM)", 1000, 8000, 4000, step=100)
eta0 = st.sidebar.slider("Initial Viscosity (Pa·s)", 0.01, 2.0, 0.05, step=0.01)
h0_nm = st.sidebar.slider("Initial Thickness (nm)", 500, 5000, 2000, step=100)
E_rate_nm = st.sidebar.slider("Evaporation Rate (nm/s)", 1, 100, 15, step=1)
R_wafer_mm = st.sidebar.slider("Wafer Radius (mm)", 50, 150, 100, step=5)

# 3. Standard Physical Unit Conversion
omega = (omega_rpm * 2 * np.pi) / 60
h0 = h0_nm * 1e-9
E = E_rate_nm * 1e-9
rho = 1000

# 4. Gelation Time Calculation & Timestep Control
if E > 0:
    t_gel = h0 / (2 * E)
else:
    t_gel = 60.0

total_time = min(60.0, t_gel)
dt = 0.5
time_steps = np.arange(0, total_time + dt, dt)

# Initialize Lists for Chart Data
t_list = []
h_center_list = []
h_edge_list = []
h_analytical_list = []

# 5. Numerical Simulation Loop
h_current = h0
for t in time_steps:
    # 1) Center - Numerical Euler Method
    eta_t = eta0 * np.exp(t / t_gel)
    K = (2 * (omega**2) * rho) / (3 * eta_t)
    
    dh_dt = -2 * K * (h_current**3) - E
    h_next = h_current + dt * dh_dt
    if h_next < 1e-12:
        h_next = 1e-12
        
    # 2) Edge - Edge Bead Adaptive Matching Algorithm
    raw_suppression = 0.015 * (R_wafer_mm / 150)**2 * (1000 / max(omega_rpm, 1000))
    edge_factor = 1.0 + min(raw_suppression, 0.0145)
    
    # 3) Analytical Validation - Classical Emslie Model (Green Line Data)
    h_ana_t = h0 / np.sqrt(1 + (4 * (omega**2) * rho * (h0**2) * t) / (3 * eta0))
    
    # Append Data (Converted to nm)
    t_list.append(t)
    h_center_list.append(float(h_current * 1e9))
    h_edge_list.append(float(h_current * edge_factor * 1e9))
    h_analytical_list.append(float(h_ana_t * 1e9))
    
    h_current = h_next

# Convert to DataFrame to Ensure Data Integrity
df_chart = pd.DataFrame({
    "Time (s)": t_list,
    "Center (Numerical Euler)": h_center_list,
    "Edge (Edge Bead Effect)": h_edge_list,
    "Analytical Limit (No Evap)": h_analytical_list
})
df_chart = df_chart.set_index("Time (s)")

# 6. UI Split Layout Render
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Real-time Film Thickness vs Time")
    # Rendering 3 traces firmly mapped within the DataFrame
    st.line_chart(df_chart)

with col2:
    st.subheader("💡 Fab Engineer Guidelines")
    st.info(f"⏳ Predicted Gelation Time ($t_{{gel}}$): {t_gel:.1f} seconds")
    
    if len(h_center_list) > 0:
        final_center_
