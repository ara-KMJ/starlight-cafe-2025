import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import unicodedata
import io

# ===============================
# 캐시 강제 초기화 (Cloud 반영 문제 방지)
# ===============================
st.cache_data.clear()

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
    color: #e0f2fe;
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
h1, h2, h3 {
    color: #bae6fd;
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
# 데이터 로딩 (한글 파일명 안전)
# ===============================
DATA_DIR = Path("data")

def load_csv(filename):
    for p in DATA_DIR.iterdir():
        if unicodedata.normalize("NFC", p.name) == unicodedata.normalize("NFC", filename):
            return pd.read_csv(p)
    st.error(f"❌ {filename} 파일을 찾을 수 없습니다.")
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

    # 날짜 채우기 + 완만 보간
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

    # 🎉 인원수 달성 이벤트
    milestones = {
        "2025-08-27": "서버 오픈 🎉",
        "2025-08-28": "100명 달성!",
        "2025-09-02": "200명 달성!",
        "2025-09-16": "300명 달성!",
        "2025-10-05": "400명 달성!",
        "2025-11-02": "500명 달성!",
        "2025-11-22": "600명 달성!",
        "2025-12-04": "700명 달성!",
    }

    for date_str, label in milestones.items():
        date = pd.to_datetime(date_str)

        fig.add_vline(
            x=date,
            line_width=1.5,
            line_dash="dot",
            line_color="#38bdf8"
        )

        fig.add_annotation(
            x=date,
            y=df["인원수(명)"].max(),
            text=label,
            showarrow=False,
            yshift=15,
            font=dict(color="#bae6fd", size=12),
            align="center"
        )

    fig.update_layout(
        font=dict(family="Malgun Gothic"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 🗓️ 서버 성장 히스토리")

    history = pd.DataFrame({
        "날짜": [
            "2025-08-27",
            "2025-08-28",
            "2025-09-02",
            "2025-09-16",
            "2025-10-05",
            "2025-11-02",
            "2025-11-22",
            "2025-12-04",
        ],
        "이벤트": [
            "서버 오픈 🎉",
            "100명 달성",
            "200명 달성",
            "300명 달성",
            "400명 달성",
            "500명 달성",
            "600명 달성",
            "700명 달성",
        ]
    })

    # 카드형 레이아웃
    for _, row in history.iterrows():
        st.markdown(f"""
        <div style="
            border-left:6px solid #38bdf8;
            padding:12px 18px;
            margin-bottom:12px;
            background-color:rgba(0,0,0,0.45);
            border-radius:6px;
        ">
            <strong style="color:#7dd3fc;">{row['날짜']}</strong>
            <span style="margin-left:12px; font-size:18px;">
                {row['이벤트']}
            </span>
        </div>
        """, unsafe_allow_html=True)

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

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["채팅 경험치", "음성 경험치"]
    )
    fig.add_bar(x=chat.index, y=chat.values, row=1, col=1)
    fig.add_bar(x=voice.index, y=voice.values, row=1, col=2)
    fig.update_layout(
        font=dict(family="Malgun Gothic"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

# ===============================
# 3️⃣ 관리진 (부서별 정리)
# ===============================
with tab3:
    st.subheader("🛡️ 관리진 목록 (부서별)")

    admins = data["admins"].copy()

    if admins.empty:
        st.error("관리진 데이터가 없습니다.")
    else:
        # ✅ 원하는 부서 순서
        dept_order = [
            "대표",
            "고위직",
            "보안",
            "안내",
            "뉴관",
            "기획",
            "홍보",
            "내전",
            "인사"
        ]

        # CSV에 있는 실제 부서 목록
        existing_depts = admins["부서"].unique().tolist()

        # 순서 적용 (없는 부서는 제외)
        ordered_depts = [d for d in dept_order if d in existing_depts]

        # 나머지 부서는 기타로
        others = [d for d in existing_depts if d not in dept_order]

        for dept in ordered_depts + (["기타"] if others else []):
            if dept == "기타":
                group = admins[admins["부서"].isin(others)]
                display_name = "기타"
            else:
                group = admins[admins["부서"] == dept]
                display_name = dept

            st.markdown(f"""
            <div style="
                border-left:6px solid #38bdf8;
                padding:12px 16px;
                margin:20px 0;
                background-color:rgba(255,255,255,0.03);
            ">
                <h3>📌 {display_name}</h3>
            </div>
            """, unsafe_allow_html=True)

            cols = st.columns(min(4, len(group)))
            for col, (_, row) in zip(cols, group.iterrows()):
                col.markdown(f"""
                <div style="
                    border:1px solid #38bdf8;
                    padding:16px;
                    text-align:center;
                    border-radius:8px;
                    background-color:rgba(0,0,0,0.4);
                ">
                    <h4>{row['이름']}</h4>
                    <p style="color:#7dd3fc;">{row['직급']}</p>
                </div>
                """, unsafe_allow_html=True)

# ===============================
# 4️⃣ 이벤트
# ===============================
with tab4:
    st.subheader("🎉 이벤트 내역")
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
