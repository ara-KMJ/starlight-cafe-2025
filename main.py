import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata
import plotly.express as px

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="2025 별빛카페 연말정산",
    layout="wide"
)

# ===============================
# 글로벌 스타일 (그라데이션)
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Noto Sans KR', sans-serif;
    background: linear-gradient(135deg, #000000 0%, #27377c 100%);
    color: #f9fafb;
}

[data-testid="stHeader"] {
    background: transparent;
}

.soft-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 16px;
    padding: 1.2em;
    margin-bottom: 1em;
    color: #f1f5f9;
}

h1, h2, h3, h4 {
    color: #ffffff;
}

.stDataFrame {
    background-color: rgba(15, 23, 42, 0.85);
}

label, p, span {
    color: #e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

# ===============================
# CSV 로더 (한글 안전)
# ===============================
def load_csv(target):
    t_nfc = unicodedata.normalize("NFC", target)
    t_nfd = unicodedata.normalize("NFD", target)
    for f in DATA_DIR.iterdir():
        if f.is_file():
            n_nfc = unicodedata.normalize("NFC", f.name)
            n_nfd = unicodedata.normalize("NFD", f.name)
            if n_nfc == t_nfc or n_nfd == t_nfd:
                return pd.read_csv(f)
    st.error(f"❌ 파일을 찾을 수 없습니다: {target}")
    return None

@st.cache_data
def member(): return load_csv("별빛카페_인원수_변화.csv")
@st.cache_data
def activity(): return load_csv("별빛카페_채팅음성.csv")
@st.cache_data
def admin(): return load_csv("현재_관리자.csv")
@st.cache_data
def event(): return load_csv("별빛카페_이벤트.csv")
@st.cache_data
def match(): return load_csv("별빛카페_내전.csv")

# ===============================
# 타이틀
# ===============================
st.title("🌌 2025 별빛카페 연말정산")
st.caption("어둠 속에서 더 선명해진 기록들")

menu = st.sidebar.radio(
    "메뉴",
    ["인원수 변화", "활동 내역", "관리진 목록", "이벤트 내역", "내전 로그"]
)

# ===============================
# 1️⃣ 인원수 변화 (완만한 보간!)
# ===============================
if menu == "인원수 변화":
    df = member()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])
        df = df.sort_values("날짜")

        # 전체 날짜 생성
        full = pd.DataFrame({
            "날짜": pd.date_range(df["날짜"].min(), df["날짜"].max(), freq="D")
        })

        full = full.merge(df, on="날짜", how="left")

        # ❗ 핵심: 선형 보간으로 자연스럽게
        full["인원수(명)"] = full["인원수(명)"].interpolate(method="linear")

        fig = px.line(
            full,
            x="날짜",
            y="인원수(명)",
            markers=True,
            title="📈 서버 인원수 변화 (자연스러운 추세)"
        )

        fig.update_layout(
            font=dict(family="Malgun Gothic", color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.15)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.15)")
        )

        st.plotly_chart(fig, use_container_width=True)

# ===============================
# 2️⃣ 활동 내역 (막대 그래프)
# ===============================
elif menu == "활동 내역":
    df = activity()
    if df is not None:
        summary = df.groupby(["이름", "종류"])["경험치"].sum().reset_index()

        st.subheader("📊 채팅 · 음성 활동량")

        fig = px.bar(
            summary,
            x="이름",
            y="경험치",
            color="종류",
            barmode="group"
        )
        fig.update_layout(
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# 3️⃣ 관리진 목록
# ===============================
elif menu == "관리진 목록":
    df = admin()
    if df is not None:
        st.subheader("🛡️ 서버 관리진")
        cols = st.columns(3)
        for i, r in df.iterrows():
            with cols[i % 3]:
                st.markdown(f"""
                <div class="soft-card">
                    <b>{r['이름']}</b><br>
                    부서: {r['부서']}<br>
                    직급: {r['직급']}
                </div>
                """, unsafe_allow_html=True)

# ===============================
# 4️⃣ 이벤트 내역
# ===============================
elif menu == "이벤트 내역":
    df = event()
    if df is not None:
        st.subheader("🎉 연간 이벤트")
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="soft-card">
                <b>{r['이벤트 이름']}</b><br>
                기간: {r['운영기간']}
            </div>
            """, unsafe_allow_html=True)

# ===============================
# 5️⃣ 내전 로그 + 승률
# ===============================
elif menu == "내전 로그":
    df = match()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])

        st.subheader("⚔️ 내전 기록")

        for _, r in df.iterrows():
            color = "#ef4444" if r["승리팀"] == "레드" else "#60a5fa"
            st.markdown(f"""
            <div class="soft-card" style="border-left:5px solid {color}">
                <b>{r['날짜'].strftime('%Y.%m.%d')} · {r['게임']}</b><br>
                참여 인원: {r['참여인원']}명<br>
                승리 팀: <span style="color:{color}">{r['승리팀']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("📊 팀별 승률")
        rate = df["승리팀"].value_counts(normalize=True) * 100
        fig = px.pie(values=rate.values, names=rate.index)
        fig.update_layout(
            font=dict(color="white"),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
