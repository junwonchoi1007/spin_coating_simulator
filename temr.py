import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🎯 Spin Coating Process Simulator & Validation")

# 1. 사이드바에 슬라이더 배치를 통한 Design-Exploration 구현
st.sidebar.header("Process Parameters")
omega_rpm = st.sidebar.slider("RPM", 1000, 8000, 3000)
eta0 = st.sidebar.slider("Viscosity (Pa·s)", 0.01, 2.0, 0.1)
h0_nm = st.sidebar.slider("Initial Thickness (nm)", 500, 5000, 2000)
E_rate_nm = st.sidebar.slider("Evaporation Rate (nm/s)", 1, 100, 20)
R_wafer_mm = st.sidebar.slider("Wafer Radius (mm)", 50, 150, 100)

# 물리 단위 변환
omega = (omega_rpm * 2 * np.pi) / 60
h0 = h0_nm * 1e-9
E = E_rate_nm * 1e-9
rho = 1000

# t_gel 연산
t_gel = h0 / (2 * E) if E > 0 else 60
total_time = min(60.0, t_gel)
dt = 0.5
time_steps = np.arange(0, total_time + dt, dt)

h_center = []
h_edge = []
h_analytical = [] # 5번 요건: Validation용 해석해 배열

h_current = h0
for t in time_steps:
    # 1) 수치해석 (Euler Method)
    eta_t = eta0 * np.exp(t / t_gel)
    K = (2 * omega**2 * rho) / (3 * eta_t)
    dh_dt = -2 * K * (h_current**3) - E
    h_next = h_current + dh_dt * dt
    if h_next < 0: h_next = 0
    
    h_center.append(h_current * 1e9)
    edge_factor = 1.0 + (0.2 * (R_wafer_mm / 150)**2)
    h_edge.append(h_current * edge_factor * 1e9)
    
    # 2) Validation View: 용매 증발이 없고 점도가 무한대인 극단적 조건($\eta \rightarrow \infty$)의 이론적 해석해
    # E -> 0, eta -> eta0 일 때의 Emslie 등의 고전 유체 해석해 수식 대입
    h_ana_t = h0 / np.sqrt(1 + (4 * omega**2 * rho * h0**2 * t) / (3 * eta0))
    h_analytical.append(h_ana_t * 1e9)
    
    h_current = h_next

# 그래프 플롯
fig, ax = plt.subplots()
ax.plot(time_steps, h_center, 'b-', label='Center (Euler)', linewidth=2)
ax.plot(time_steps, h_edge, 'r--', label='Edge (Edge Bead)', linewidth=2)
ax.plot(time_steps, h_analytical, 'g:', label='Analytical Limit (No Evap)', linewidth=2) # 검증선 추가

ax.set_xlim(0, 60)
ax.set_ylim(0, h0_nm + 500)
ax.set_xlabel("Time t (s)")
ax.set_ylabel("Thickness h (nm)")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# 6번 요건: Fab Engineer를 위한 가이드라인 자동 출력
st.subheader("💡 Process Design Insight (for Fab Engineers)")
st.write(f"1. Predicted **Gelation Time ($t_{{gel}}$)** is **{t_gel:.1f} seconds**.")
st.write("2. To achieve higher uniformity, consider reducing the initial viscosity or increasing the solvent concentration to artificially delay the gelation point.")