import streamlit as st
import numpy as np
import pandas as pd

# 1. 웹 브라우저 전체 레이아웃 및 제목 설정 (원본 복구)
st.set_page_config(layout="wide")
st.title("🎯 Spin Coating Process Simulator & Validation")

# 2. 사이드바에 입력 변수(Design-Exploration Mode) 슬라이더 배치
st.sidebar.header("🔧 공정 변수 설정 (Process Parameters)")
omega_rpm = st.sidebar.slider("회전 속도 (RPM)", 1000, 8000, 3000, step=100)
eta0 = st.sidebar.slider("초기 점도 Viscosity (Pa·s)", 0.01, 2.0, 0.1, step=0.01)
h0_nm = st.sidebar.slider("초기 박막 두께 Thickness (nm)", 500, 5000, 2000, step=100)
E_rate_nm = st.sidebar.slider("용매 증발 속도 Evaporation Rate (nm/s)", 1, 100, 20, step=1)
R_wafer_mm = st.sidebar.slider("웨이퍼 반지름 Wafer Radius (mm)", 50, 150, 100, step=5)

# 3. 수치해석용 물리 표준 단위 변환 (m, rad/s)
omega = (omega_rpm * 2 * np.pi) / 60
h0 = h0_nm * 1e-9
E = E_rate_nm * 1e-9
rho = 1000  # 유체 밀도 가정 (kg/m^3)

# 4. [요청 반영] t_gel(겔화 시간)에 맞춰 그래프 시간 범위를 60초가 안 되게 자동 조절
if E > 0:
    t_gel = h0 / (2 * E)
    # 굳이 60초까지 갈 필요 없이, 변화가 끝나는 겔화 시간의 1.2배까지만 콤팩트하게 화면 조절
    display_time = min(60.0, t_gel * 1.2)
else:
    t_gel = 60.0
    display_time = 30.0

dt = 0.5
time_steps = np.arange(0, display_time + dt, dt)

# 데이터 저장용 배열 초기화
t_list = []
h_center_list = []
h_edge_list = []
h_analytical_list = []  # 과제 5번 요건: Validation View용 이론적 해석해 배열

# 5. 시간 전진 루프 (수치해석 및 검증해 동시 연산)
h_current = h0
for t in time_steps:
    # 1) Center (중앙부 - Euler Method 수치해석)
    eta_t = eta0 *
