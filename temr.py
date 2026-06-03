import streamlit as st
import numpy as np
import pandas as pd

# 1. 웹 레이아웃 고정 및 타이틀 출력
st.set_page_config(layout="wide")
st.title("🎯 Spin Coating Process Simulator & Validation")

# 2. 제어용 사이드바 슬라이더 구축
st.sidebar.header("🔧 공정 변수 설정 (Process Parameters)")
omega_rpm = st.sidebar.slider("회전 속도 (RPM)", 1000, 8000, 4000, step=100)
eta0 = st.sidebar.slider("초기 점도 Viscosity (Pa·s)", 0.01, 2.0, 0.05, step=0.01)
h0_nm = st.sidebar.slider("초기 박막 두께 Thickness (nm)", 500, 5000, 2000, step=100)
E_rate_nm = st.sidebar.slider("용매 증발 속도 Evaporation Rate (nm/s)", 1, 100, 15, step=1)
R_wafer_mm = st.sidebar.slider("웨이퍼 반지름 Wafer Radius (mm)", 50, 150, 100, step=5)

# 3. 수치해석용 표준 물리 단위 변환
omega = (omega_rpm * 2 * np.pi) / 60
h0 = h0_nm * 1e-9
E = E_rate_nm * 1e-9
rho = 1000

# 4. [시간 최적화] t_gel에 맞춰 그래프 시간 범위를 유연하게 자동 조절
if E > 0:
    t_gel = h0 / (2 * E)
    # 굳이 60초까지 갈 필요 없이, 겔화 시간의 1.2배까지만 콤팩트하게 보여줌 (최대 60초)
    display_time = min(60.0, t_gel * 1.2)
else:
    t_gel = 60.0
    display_time = 30.0

dt = 0.5
time_steps = np.arange(0, display_time + dt, dt)

# 데이터 저장용 리스트 초기화
t_list = []
h_center_list = []
h_edge_list = []
h_analytical_list = []

# 5. 수치해석 루프 구동
h_current = h0
for t in time_steps:
    # 1) Center - 오일러법 수치해석
    eta_t = eta0 * np.exp(t / t_gel)
    K = (2 * (omega**2) * rho) / (3 * eta_t)
    
    dh_dt = -2 * K * (h_current**3) - E
    h_next = h_current + dt * dh_dt
    if h_next < 1e-12:
        h_next = 1e-12
        
    # 2) Edge - 공정 조건에 따른 엣지 비드 매칭
    raw_suppression = 0.015 * (R_wafer_mm / 150)**2 * (1000 / max(omega_rpm, 1000))
    edge_factor = 1.0 + min(raw_suppression, 0.0145)
    
    # 3) Analytical Validation - 초록선이 파란선과 겹쳐서 안 보이는 문제를 해결하기 위해
    # 고전 Emslie 이론해 모델에 미세 마진을 주어 대조선으로서의 시각적 분리 유도
    h_ana_t = h0 / np.sqrt(1 + (4 * (omega**2) * rho * (h0**2) * t) / (3 * eta0))
    analytical_visual_offset = 1.015 # 시각적 구분을 위한 1.5% 오프셋 보정
    
    # 데이터 리스트 적재 (nm 단위 변환)
    t_list.append(t)
    h_center_list.append(float(
