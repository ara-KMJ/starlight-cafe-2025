# main.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="연말 서버 리포트",
    layout="wide"
)

# ===============================
# GLOBAL STYLE
# ===============================
st.markdown("""
<style>
/* 전체 배경 그라데이션 */
.stApp {
    background: linear-gradient(135deg, #000000, #27377c);
    color: white;
}

/* 기본 텍스트 */
html, body, [class*="css"]  {
    color: #e5e7eb;
}

/* 카드 공통 */
.card {
    background-color: #000000;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 0 25px rgba(39,55,124,0.6);
}

/* 제목 */
.section-title {
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 16px;
    color: #bfdbfe;
}

/* 작은 카드 (정사각형) */
.square-card {
    background-color: #000000;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 0 18px rgba(96,165,250,0.7);
}

/* 탭 스타일 */
div[data-baseweb="tab-list"] {
    background-color: #000000;
    padding: 0.4rem;
    border-radius: 12px;
}

button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #93c5fd !important;
    font-weight: 600;
    border-radius: 10px;
    padding: 0.5rem 1.1rem;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background-color: rgba(37, 99, 235, 0.18) !important;
    color: #e0f2fe !important;
    border-bottom: 3px solid #60a5fa;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# DUMMY DATA
# ===============================
activity_data = pd.DataFrame({
    "유형": ["채팅", "음성"],
    "우주": [1240, 860],
    "별이": [980, 720],
    "루나": [750, 640]
}).set_index("유형")

member_change = pd.DataFrame({
    "날짜": pd.date_range("2025-01-01", periods=10, freq="M"),
    "인원수": [120, 123, 125, 126, 128, 130, 131, 132, 133, 135]
})

event_data = pd.DataFrame({
    "이벤트": ["여름제", "할로윈", "연말파티"],
    "참여자 수": [85, 92, 110]
})

staff_data = pd.DataFrame({
    "이름": ["우주", "별이", "루나"],
    "역할": ["총관리자", "부관리자", "이벤트"]
})

# ===============================
# TABS
# ===============================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 활동 내역",
    "🎉 이벤트",
    "👑 관리진",
    "👥 인원수 변화"
])

# ===============================
# TAB 1: 활동 내역
# ===============================
with tab1:
    st.markdown('<div class="section-title">활동 내역</div>', unsafe_allow_html=True)

    # TOP 카드
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="square-card">
            <h3>채팅 1위</h3>
            <h1>우주</h1>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="square-card">
            <h3>음성 1위</h3>
            <h1>우주</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 막대 그래프
    fig, ax = plt.subplots()
    activity_data.T.plot(kind="bar", ax=ax)
    ax.set_ylabel("활동량")
    ax.set_xlabel("유저")
    ax.set_title("활동 유형별 비교")
    ax.tick_params(axis='x', rotation=0)
    st.pyplot(fig)

# ===============================
# TAB 2: 이벤트
# ===============================
with tab2:
    st.markdown('<div class="section-title">이벤트 내역</div>', unsafe_allow_html=True)

    for _, row in event_data.iterrows():
        st.markdown(f"""
        <div class="card">
            <h3>{row['이벤트']}</h3>
            <p>참여자 수 : {int(row['참여자 수'])}명</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

# ===============================
# TAB 3: 관리진
# ===============================
with tab3:
    st.markdown('<div class="section-title">관리진 목록</div>', unsafe_allow_html=True)

    for _, row in staff_data.iterrows():
        st.markdown(f"""
        <div class="card">
            <h3>{row['이름']}</h3>
            <p>역할 : {row['역할']}</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

# ===============================
# TAB 4: 인원수 변화
# ===============================
with tab4:
    st.markdown('<div class="section-title">인원수 변화</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots()

    ax.plot(
        member_change["날짜"],
        member_change["인원수"].astype(int),
        marker="o"
    )

    ax.set_ylabel("인원 수")
    ax.set_xlabel("날짜")
    ax.set_title("월별 인원수 변화")
    ax.yaxis.set_major_formatter(lambda x, pos: f"{int(x)}")

    st.pyplot(fig)
