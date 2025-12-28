import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="별빛카페 연말 리포트", layout="wide")

# ======================
# STYLE
# ======================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #000000, #27377c);
    color: white;
}
.section-title {
    font-size: 28px;
    font-weight: 800;
    color: #bae6fd;
    margin-bottom: 20px;
}
.square {
    background:#020617;
    border-radius:16px;
    padding:20px;
    text-align:center;
    box-shadow:0 0 20px rgba(56,189,248,0.6);
}
.card {
    background:#020617;
    border-radius:16px;
    padding:18px;
    margin-bottom:12px;
}
div[data-baseweb="tab-list"] {
    background:#000000;
}
button[data-baseweb="tab"] {
    color:#7dd3fc !important;
    font-weight:600;
}
button[aria-selected="true"] {
    background:rgba(125,211,252,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================
activity = pd.read_csv("/mnt/data/별빛카페_채팅음성.csv")
events = pd.read_csv("/mnt/data/별빛카페_이벤트.csv")
staff = pd.read_csv("/mnt/data/현재_관리자.csv")
members = pd.read_csv("/mnt/data/별빛카페_인원수_변화.csv")

members["날짜"] = pd.to_datetime(members["날짜"])

# ======================
# 인원수 날짜 보정 (핵심)
# ======================
full_dates = pd.date_range(
    start=members["날짜"].min(),
    end=members["날짜"].max(),
    freq="D"
)

members_full = (
    members.set_index("날짜")
    .reindex(full_dates)
    .interpolate(method="linear")
    .rolling(7, min_periods=1).mean()
    .round()
    .astype(int)
    .reset_index()
)

members_full.columns = ["날짜", "인원수"]

# ======================
# MVP 계산
# ======================
chat_top = activity.groupby("이름")["채팅"].sum().idxmax()
voice_top = activity.groupby("이름")["음성"].sum().idxmax()

# ======================
# TABS
# ======================
t1, t2, t3, t4 = st.tabs(["📊 활동", "🎉 이벤트", "👑 관리진", "👥 인원수 변화"])

# ======================
# TAB 1 활동
# ======================
with t1:
    st.markdown('<div class="section-title">활동 내역</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='square'><h3>채팅 1위</h3><h1>{chat_top}</h1></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='square'><h3>음성 1위</h3><h1>{voice_top}</h1></div>", unsafe_allow_html=True)

    fig, ax = plt.subplots()
    activity.set_index("이름")[["채팅", "음성"]].plot(kind="bar", ax=ax)
    ax.set_facecolor("#020617")
    fig.patch.set_facecolor("#020617")
    ax.tick_params(colors="white")
    ax.set_ylabel("활동량", color="white")
    st.pyplot(fig)

# ======================
# TAB 2 이벤트
# ======================
with t2:
    st.markdown('<div class="section-title">이벤트</div>', unsafe_allow_html=True)
    for _, r in events.iterrows():
        st.markdown(f"<div class='card'><h3>{r['이벤트명']}</h3><p>참여자 {int(r['참여자'])}</p></div>", unsafe_allow_html=True)

# ======================
# TAB 3 관리진
# ======================
with t3:
    st.markdown('<div class="section-title">관리진</div>', unsafe_allow_html=True)
    for _, r in staff.iterrows():
        st.markdown(f"<div class='card'><h3>{r['이름']}</h3><p>{r['역할']}</p></div>", unsafe_allow_html=True)

# ======================
# TAB 4 인원수 변화
# ======================
with t4:
    st.markdown('<div class="section-title">인원수 변화</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots()
    ax.plot(
        members_full["날짜"],
        members_full["인원수"],
        linewidth=3
    )
    ax.set_facecolor("#020617")
    fig.patch.set_facecolor("#020617")
    ax.tick_params(colors="white")
    ax.set_ylabel("인원수", color="white")
    ax.set_xlabel("날짜", color="white")
    st.pyplot(fig)
