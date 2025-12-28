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
# 전체 스타일 (강한 대비)
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Noto Sans KR', sans-serif;
    background: linear-gradient(135deg, #000000 0%, #27377c 100%);
    color: #ffffff;
}

h1, h2, h3 {
    font-weight: 800;
}

/* 랭킹 메인 박스 */
.rank-square {
    background: rgba(10, 15, 35, 0.95);
    border: 2px solid rgba(147, 197, 253, 0.6);
    border-radius: 18px;
    aspect-ratio: 1 / 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 0 40px rgba(59, 130, 246, 0.35);
}

.rank-title {
    font-size: 1.4rem;
    color: #93c5fd;
}

.rank-name {
    font-size: 2.6rem;
    margin-top: 0.4em;
}

/* 정보 카드 */
.info-card {
    background: rgba(15, 23, 42, 0.9);
    border-radius: 14px;
    padding: 1.2em;
    margin-bottom: 1em;
}

/* 그래프 배경 제거 */
.js-plotly-plot {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

# ===============================
# CSV 로더 (한글 완전 대응)
# ===============================
def load_csv(filename):
    t_nfc = unicodedata.normalize("NFC", filename)
    t_nfd = unicodedata.normalize("NFD", filename)

    for f in DATA_DIR.iterdir():
        if f.is_file():
            n_nfc = unicodedata.normalize("NFC", f.name)
            n_nfd = unicodedata.normalize("NFD", f.name)
            if n_nfc == t_nfc or n_nfd == t_nfd:
                return pd.read_csv(f)

    st.error(f"❌ 파일을 찾을 수 없습니다: {filename}")
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
st.caption("숫자로 남긴 우리의 한 해")

menu = st.sidebar.radio(
    "메뉴",
    ["인원수 변화", "활동 내역", "관리진 목록", "이벤트 내역", "내전 로그"]
)

# ===============================
# 1️⃣ 인원수 변화
# ===============================
if menu == "인원수 변화":
    df = member()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])
        df = df.sort_values("날짜")

        full = pd.DataFrame({
            "날짜": pd.date_range(df["날짜"].min(), df["날짜"].max(), freq="D")
        })
        full = full.merge(df, on="날짜", how="left")

        # ❗ 자연스러운 보간 + 자연수
        full["인원수(명)"] = (
            full["인원수(명)"]
            .interpolate(method="linear")
            .astype(int)
        )

        fig = px.line(
            full,
            x="날짜",
            y="인원수(명)",
            markers=True,
            title="📈 서버 인원수 변화"
        )

        fig.update_layout(
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.15)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.15)")
        )

        st.plotly_chart(fig, use_container_width=True)

# ===============================
# 2️⃣ 활동 내역 (완전 개편)
# ===============================
elif menu == "활동 내역":
    df = activity()
    if df is not None:
        total = (
            df.groupby(["이름", "종류"])["경험치"]
            .sum()
            .reset_index()
        )

        chat_top = total[total["종류"] == "채팅"].sort_values("경험치", ascending=False).iloc[0]["이름"]
        voice_top = total[total["종류"] == "음성"].sort_values("경험치", ascending=False).iloc[0]["이름"]

        st.subheader("🏆 2025 활동 1위")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="rank-square">
                <div class="rank-title">채팅 1위</div>
                <div class="rank-name">{chat_top}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="rank-square">
                <div class="rank-title">음성 1위</div>
                <div class="rank-name">{voice_top}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📊 전체 활동 경험치")

        fig = px.bar(
            total,
            x="이름",
            y="경험치",
            color="종류",
            barmode="group"
        )

        fig.update_layout(
            height=520,
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, use_container_width=True)

# ===============================
# 3️⃣ 관리진
# ===============================
elif menu == "관리진 목록":
    df = admin()
    if df is not None:
        st.subheader("🛡️ 현재 관리진")
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="info-card">
                <b>{r['이름']}</b><br>
                {r['부서']} · {r['직급']}
            </div>
            """, unsafe_allow_html=True)

# ===============================
# 4️⃣ 이벤트
# ===============================
elif menu == "이벤트 내역":
    df = event()
    if df is not None:
        st.subheader("🎉 연간 이벤트")
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="info-card">
                <b>{r['이벤트 이름']}</b><br>
                운영 기간: {r['운영기간']}
            </div>
            """, unsafe_allow_html=True)

# ===============================
# 5️⃣ 내전 로그
# ===============================
elif menu == "내전 로그":
    df = match()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])

        st.subheader("⚔️ 내전 기록")
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="info-card">
                <b>{r['날짜'].strftime('%Y.%m.%d')} · {r['게임']}</b><br>
                참여 인원: {r['참여인원']}명<br>
                승리 팀: {r['승리팀']}
            </div>
            """, unsafe_allow_html=True)

        st.subheader("📊 팀별 승률")
        rate = df["승리팀"].value_counts(normalize=True) * 100
        fig = px.pie(values=rate.values, names=rate.index)
        fig.update_layout(font=dict(color="white"), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
