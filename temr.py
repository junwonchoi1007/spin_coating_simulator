import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 레이아웃 및 제목 설정
st.set_page_config(layout="wide")
st.title("🎯 Spin Coating Process Simulator & Validation")

# 2. 사이드바 제어 슬라이더 구성 (Design-Exploration Mode)
st.sidebar.header("🔧 공정 변수 설정 (Process Parameters)")
omega_rpm = st.sidebar.slider("회전 속도 (RPM)", 1000, 8000, 3000, step=100)
eta0 = st.sidebar.slider("초기 점도 Viscosity (Pa·s)", 0.01, 2.0, 0.1, step=0.01)
h0_nm = st.sidebar.slider("초기 박막 두께 Thickness (nm)", 500, 5000, 2000, step=100)
E_rate_nm = st.sidebar.slider("용매 증발 속도 Evaporation Rate (nm/s)", 1, 100, 20, step=1)
R_wafer_mm = st.sidebar.slider("웨이퍼 반지름 Wafer Radius (mm)", 50, 150, 100, step=5)

# 3. 물리 단위 변환
omega = (omega_rpm * 2 * np.pi) / 60
h0 = h0_nm * 1e-9
E = E_rate_nm * 1e-9
rho = 1000

# 4. t_gel 연산 및 시간 영역 설정
if E > 0:
    t_gel = h0 / (2 * E)
else:
    t_gel = 60.0

total_time = min(60.0, t_gel)
dt = 0.5
time_steps = np.arange(0, total_time + dt, dt)

h_center = []
h_edge = []
h_analytical = []

# 5. 수치해석 루프 실행
h_current = h0
for t in time_steps:
    # 1) Center - 수치해석 오일러법
    eta_t = eta0 * np.exp(t / t_gel)
    K = (2 * (omega**2) * rho) / (3 * eta_t)
    
    dh_dt = -2 * K * (h_current**3) - E
    h_next = h_current + dh_dt * dt
    if h_next < 0: 
        h_next = 0
    
    h_center.append(h_current * 1e9)
    
    # 2) Edge - Edge Bead 효과 모사
    edge_factor = 1.0 + (0.2 * (R_wafer_mm / 150)**2)
    h_edge.append(h_current * edge_factor * 1e9)
    
    # 3) Validation - 고전 유체역학 이론적 해석해 (Emslie Model)
    h_ana_t = h0 / np.sqrt(1 + (4 * (omega**2) * rho * (h0**2) * t) / (3 * eta0))
    h_analytical.append(h_ana_t * 1e9)
    
    h_current = h_next

# 6. 화면 분할 출력
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 실시간 두께 변화 그래프 (Thickness vs Time)")
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(time_steps, h_center, 'b-', label='Center (Numerical Euler)', linewidth=2.5)
    ax.plot(time_steps, h_edge, 'r--', label='Edge (Edge Bead Effect)', linewidth=2.5)
    ax.plot(time_steps, h_analytical, 'g:', label='Analytical Limit (No Evap Mode)', linewidth=2)
    
    ax.set_xlim(0, 60)
    ax.set_ylim(0, h0_nm + 500)
    ax.set_xlabel("Time t (s)")
    ax.set_ylabel("Thickness h (nm)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')
    
    st.pyplot(fig)

with col2:
    st.subheader("💡 Fab Engineer 공정 가이드라인")
    st.info(f"⏳ **예측된 겔화 시간 (Gelation Time, $t_{{gel}}$):** \n\n **{t_gel:.1f} 초 (seconds)**")
    
    final_center_val = h_center[-1]
    final_edge_val = h_edge[-1]
    uniformity_err = (abs(final_center_val - final_edge_val) / final_center_val) * 100
    
    st.write("---")
    st.markdown("### 🎯 최종 균일도 평가 결과")
    st.write(f"- 중앙부 최종 두께: {final_center_val:.1f} nm")
    st.write(f"- 가장자리 최종 두께: {final_edge_val:.1f} nm")
    
    if uniformity_err <= 2.0:
        st.success(f"🎯 Target Met! 균일도 에러 오차 범위가 ±{uniformity_err:.2f}% 내에 도달했습니다.")
    else:
        st.error(f"❌ Target Failed! 반경 균일도 오차가 ±{uniformity_err:.2f}%로 스펙을 초과했습니다. 공정 변수를 재조정하십시오.")
