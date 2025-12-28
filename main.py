import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import unicodedata
import io

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="2025 별빛카페 연말정산",
    layout="wide"
)

# ===============================
# 전체 스타일 (배경 / 글씨)
# ===============================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #000000, #27377c);
}
html, body, [class*="css"] {
    color: #bae6fd;
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
h1, h2, h3 {
    color: #e0f2fe;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# 타이틀
# ===============================
st.markdown("""
<h1 style="text-align:center; font-size:48px; font-weight:900; margin-bottom:40px;">
✨ 2025 별빛카페 연말정산 ✨
</h1>
""", unsafe_allow_html=True)

# ===============================
# 파일 로딩 (한글 안전)
# ===============================
DATA_DIR = Path("data")

def load_csv(filename):
    for p in DATA_DIR.iterdir():
        if unicodedata.normalize("NFC", p.name) == unicodedata.normalize("NFC", filename):
            return pd.read_csv(p)
    st.error(f"{filename} 파일을 찾을 수 없습니다.")
    return pd.DataFrame()

@st.cache_data
def load_all():
    return {
        "members": load_csv("별빛카페_인원수_변화.csv"),
        "activity": load_csv("별빛카페_채팅음성.csv"),
        "admins": load_csv("현재_관리자.csv"),
        "events": load_csv("별빛카페_이벤트.csv"),
        "wars": load_csv("별빛카페_내전.csv"),
    }

with st.spinner("데이터 불러오는 중..."):
    data = load_all()

# ===============================
# 탭 구성
# ===============================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 인원수 변화",
    "🔥 활동 내역",
    "🛡️ 관리진",
    "🎉 이벤트",
    "🎮 내전 로그"
])

# ===============================
# 1️⃣ 인원수 변화
# ===============================
with tab1:
    df = data["members"].copy()
    df["날짜"] = pd.to_datetime(df["날짜"])
    df = df.sort_values("날짜")

    # 날짜 채우기 (완만 보간)
    full_dates = pd.date_range("2025-08-27", "2025-12-24")
    df = df.set_index("날짜").reindex(full_dates)
    df["인원수(명)"] = df["인원수(명)"].interpolate().round().astype(int)
    df = df.reset_index().rename(columns={"index": "날짜"})

    fig = px.line(
        df,
        x="날짜",
        y="인원수(명)",
        markers=True,
        title="서버 인원수 변화"
    )
    fig.update_layout(
        font=dict(family="Malgun Gothic"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

# ===============================
# 2️⃣ 활동 내역
# ===============================
with tab2:
    act = data["activity"]

    chat = act[act["종류"] == "채팅"].groupby("이름")["경험치"].sum()
    voice = act[act["종류"] == "음성"].groupby("이름")["경험치"].sum()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="border:2px solid #38bdf8; padding:30px; text-align:center;">
        <h3>채팅 1위</h3>
        <h2>{chat.idxmax()}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="border:2px solid #38bdf8; padding:30px; text-align:center;">
        <h3>음성 1위</h3>
        <h2>{voice.idxmax()}</h2>
        </div>
        """, unsafe_allow_html=True)

    fig = make_subplots(rows=1, cols=2, subplot_titles=["채팅 경험치", "음성 경험치"])
    fig.add_bar(x=chat.index, y=chat.values, row=1, col=1)
    fig.add_bar(x=voice.index, y=voice.values, row=1, col=2)
    fig.update_layout(font=dict(family="Malgun Gothic"))
    st.plotly_chart(fig, use_container_width=True)

# ===============================
# 3️⃣ 관리진
# ===============================
with tab3:
    st.dataframe(data["admins"], use_container_width=True)

# ===============================
# 4️⃣ 이벤트
# ===============================
with tab4:
    st.dataframe(data["events"], use_container_width=True)

# ===============================
# 5️⃣ 내전 로그 + 승률
# ===============================
with tab5:
    war = data["wars"]

    st.subheader("🎮 내전 로그")
    st.dataframe(war, use_container_width=True)

    win_rate = war["승리팀"].value_counts(normalize=True) * 100
    win_df = win_rate.reset_index()
    win_df.columns = ["팀", "승률"]

    fig = px.bar(
        win_df,
        x="팀",
        y="승률",
        color="팀",
        color_discrete_map={
            "레드": "red",
            "블루": "blue"
        },
        title="내전 승률 (%)"
    )
    fig.update_layout(
        font=dict(family="Malgun Gothic"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)
