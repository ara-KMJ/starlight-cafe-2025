import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="2025 별빛카페 연말정산",
    layout="wide"
)

# ===============================
# TITLE
# ===============================
st.markdown("""
<h1 style="
    text-align:center;
    font-size:48px;
    font-weight:900;
    margin-top:10px;
    margin-bottom:40px;
    color:#bae6fd;
">
✨ 2025 별빛카페 연말정산 ✨
</h1>
""", unsafe_allow_html=True)

# ===============================
# STYLE
# ===============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #000000, #27377c);
}
* {
    color: #e0f2fe !important;
    font-family: 'Noto Sans KR','Malgun Gothic',sans-serif;
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
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    members = pd.read_csv("data/별빛카페_인원수_변화.csv")
    activity = pd.read_csv("data/별빛카페_채팅음성.csv")
    events = pd.read_csv("data/별빛카페_이벤트.csv")
    staff = pd.read_csv("data/현재_관리자.csv")
    scrim = pd.read_csv("data/별빛카페_내전.csv")
    return members, activity, events, staff, scrim

with st.spinner("데이터 불러오는 중..."):
    members, activity, events, staff, scrim = load_data()

# ===============================
# 인원수 보정 (완만 + 자연수)
# ===============================
members["날짜"] = pd.to_datetime(members["날짜"])
full_dates = pd.date_range(
    members["날짜"].min(),
    members["날짜"].max(),
    freq="D"
)

members_full = (
    members.set_index("날짜")
    .reindex(full_dates)
    .interpolate()
    .rolling(7, min_periods=1)
    .mean()
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
# 내전 승률
# ===============================
win_rate = (
    scrim["승리팀"]
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)

# ===============================
# TABS
# ===============================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 활동 내역",
    "🎉 이벤트",
    "👑 관리진",
    "👥 인원수 변화",
    "⚔️ 내전 로그"
])

# ===============================
# TAB 1 활동 내역
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
            f"<div class='card'><h3>{r['이벤트 이름']}</h3><p>{r['운영기간']}</p></div>",
            unsafe_allow_html=True
        )

# ===============================
# TAB 3 관리진
# ===============================
with tab3:
    st.markdown('<div class="section-title">관리진 목록</div>', unsafe_allow_html=True)
    for _, r in staff.iterrows():
        st.markdown(
            f"<div class='card'><h3>{r['이름']}</h3><p>{r['부서']} | {r['직급']}</p></div>",
            unsafe_allow_html=True
        )

# ===============================
# TAB 4 인원수 변화
# ===============================
with tab4:
    st.markdown('<div class="section-title">인원수 변화</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=members_full["날짜"],
        y=members_full["인원수"],
        mode="lines",
        line=dict(width=4, color="#7dd3fc"),
        fill="tozeroy"
    ))

    fig.update_layout(
        paper_bgcolor="#020617",
        plot_bgcolor="#020617",
        yaxis=dict(tickformat=",d"),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# ===============================
# TAB 5 내전 로그
# ===============================
with tab5:
    st.markdown('<div class="section-title">내전 로그</div>', unsafe_allow_html=True)

    # 승률 카드
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='square'><h3>레드팀 승률</h3><h1>{win_rate.get('레드', 0)}%</h1></div>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div class='square'><h3>블루팀 승률</h3><h1>{win_rate.get('블루', 0)}%</h1></div>",
            unsafe_allow_html=True
        )

    # 승률 그래프 (색 지정)
    fig = go.Figure()
    fig.add_bar(
        x=["레드팀"],
        y=[win_rate.get("레드", 0)],
        marker_color="#ef4444",
        name="레드팀"
    )
    fig.add_bar(
        x=["블루팀"],
        y=[win_rate.get("블루", 0)],
        marker_color="#3b82f6",
        name="블루팀"
    )

    fig.update_layout(
        barmode="group",
        paper_bgcolor="#020617",
        plot_bgcolor="#020617",
        yaxis=dict(title="승률 (%)", range=[0, 100]),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 내전 로그 카드
    for _, r in scrim.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <h3>{r['게임']}</h3>
                <p>📅 날짜: {r['날짜']}</p>
                <p>👥 참여 인원: {r['참여인원']}명</p>
                <p>🏆 승리팀: <b>{r['승리팀']}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )
