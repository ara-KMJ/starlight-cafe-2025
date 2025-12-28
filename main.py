import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="2025 별빛카페 연말정산",
    layout="wide"
)

# ===============================
# GLOBAL STYLE
# ===============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #000000, #27377c);
    color: white;
}
h1, h2, h3, h4, p, span, div {
    color: #e0f2fe;
}
.section-title {
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 20px;
}
.square {
    background:#020617;
    border-radius:18px;
    padding:24px;
    text-align:center;
    box-shadow:0 0 20px rgba(125,211,252,0.5);
}
.card {
    background:#020617;
    border-radius:16px;
    padding:18px;
    margin-bottom:14px;
}
div[data-baseweb="tab-list"] {
    background:#000000;
}
button[data-baseweb="tab"] {
    color:#7dd3fc !important;
    font-weight:700;
}
button[aria-selected="true"] {
    background:rgba(125,211,252,0.25) !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA LOAD
# ===============================
@st.cache_data
def load_data():
    members = pd.read_csv("data/별빛카페_인원수_변화.csv")
    activity = pd.read_csv("data/별빛카페_채팅음성.csv")
    events = pd.read_csv("data/별빛카페_이벤트.csv")
    staff = pd.read_csv("data/현재_관리자.csv")
    return members, activity, events, staff

with st.spinner("데이터 불러오는 중..."):
    members, activity, events, staff = load_data()

# ===============================
# 인원수 날짜 보정 (완만)
# ===============================
members["날짜"] = pd.to_datetime(members["날짜"])

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

# ===============================
# 활동 TOP
# ===============================
chat_top = (
    activity[activity["종류"] == "채팅"]
    .groupby("이름")["경험치"]
    .sum()
    .idxmax()
)

voice_top = (
    activity[activity["종류"] == "음성"]
    .groupby("이름")["경험치"]
    .sum()
    .idxmax()
)

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
# TAB 1 활동
# ===============================
with tab1:
    st.markdown('<div class="section-title">활동 내역</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='square'><h3>채팅 1위</h3><h1>{chat_top}</h1></div>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div class='square'><h3>음성 1위</h3><h1>{voice_top}</h1></div>",
            unsafe_allow_html=True
        )

    summary = activity.groupby(["이름", "종류"])["경험치"].sum().unstack(fill_value=0)

    fig = go.Figure()
    for col in summary.columns:
        fig.add_bar(
            x=summary.index,
            y=summary[col],
            name=col
        )

    fig.update_layout(
        barmode="group",
        paper_bgcolor="#020617",
        plot_bgcolor="#020617",
        font=dict(color="#e0f2fe", family="Malgun Gothic"),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# ===============================
# TAB 2 이벤트
# ===============================
with tab2:
    st.markdown('<div class="section-title">이벤트 내역</div>', unsafe_allow_html=True)

    for _, r in events.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <h3>{r['이벤트 이름']}</h3>
                <p>운영 기간: {r['운영기간']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ===============================
# TAB 3 관리진
# ===============================
with tab3:
    st.markdown('<div class="section-title">관리진 목록</div>', unsafe_allow_html=True)

    for _, r in staff.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <h3>{r['이름']}</h3>
                <p>{r['부서']} | {r['직급']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ===============================
# TAB 4 인원수 변화
# ===============================
with tab4:
    st.markdown('<div class="section-title">인원수 변화</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=members_full["날짜"],
            y=members_full["인원수"],
            mode="lines",
            line=dict(width=4, color="#7dd3fc"),
            fill="tozeroy"
        )
    )

    fig.update_layout(
        paper_bgcolor="#020617",
        plot_bgcolor="#020617",
        font=dict(color="#e0f2fe", family="Malgun Gothic"),
        yaxis=dict(tickformat=",d"),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
