import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata
import io
import plotly.express as px

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="2025 별빛카페 연말정산",
    layout="wide"
)

# ===============================
# 글로벌 스타일 (깔롱&쌈뽕)
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}

.title {
    font-size: 42px;
    font-weight: 800;
}
.subtitle {
    color: #9ca3af;
    margin-bottom: 2em;
}

.card {
    padding: 1.2em;
    border-radius: 18px;
    background: linear-gradient(135deg, #020617, #020617);
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    margin-bottom: 1em;
}

.card h3 {
    margin: 0;
    font-size: 20px;
}

.card p {
    margin: 0.3em 0 0 0;
    color: #d1d5db;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

# ===============================
# CSV 로더 (NFC/NFD)
# ===============================
def load_csv_by_normalized_name(target_name):
    target_nfc = unicodedata.normalize("NFC", target_name)
    target_nfd = unicodedata.normalize("NFD", target_name)

    for file in DATA_DIR.iterdir():
        if not file.is_file():
            continue
        name_nfc = unicodedata.normalize("NFC", file.name)
        name_nfd = unicodedata.normalize("NFD", file.name)
        if name_nfc == target_nfc or name_nfd == target_nfd:
            return pd.read_csv(file)

    st.error(f"❌ 파일을 찾을 수 없습니다: {target_name}")
    return None

@st.cache_data
def load_member(): return load_csv_by_normalized_name("별빛카페_인원수_변화.csv")
@st.cache_data
def load_activity(): return load_csv_by_normalized_name("별빛카페_채팅음성.csv")
@st.cache_data
def load_admin(): return load_csv_by_normalized_name("현재_관리자.csv")
@st.cache_data
def load_event(): return load_csv_by_normalized_name("별빛카페_이벤트.csv")
@st.cache_data
def load_match(): return load_csv_by_normalized_name("별빛카페_내전.csv")

# ===============================
# 타이틀
# ===============================
st.markdown('<div class="title">🌌 2025 별빛카페 연말정산</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">한 해 동안의 성장과 기록</div>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "📂 메뉴",
    ["인원수 변화", "활동 내역", "관리진 목록", "이벤트 내역", "내전 로그"]
)

# ===============================
# 1️⃣ 인원수 변화
# ===============================
if menu == "인원수 변화":
    df = load_member()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])
        df = df.sort_values("날짜")

        START, END = pd.to_datetime("2025-08-27"), pd.to_datetime("2025-12-24")
        DAILY = 6.51

        dates = pd.date_range(START, END, freq="D")
        full = pd.DataFrame({"날짜": dates}).merge(df, on="날짜", how="left")

        base_date, base_val = df.iloc[0]["날짜"], df.iloc[0]["인원수(명)"]

        def estimate(row):
            if not pd.isna(row["인원수(명)"]):
                return row["인원수(명)"]
            return round(base_val + (row["날짜"] - base_date).days * DAILY, 1)

        full["인원수(명)"] = full.apply(estimate, axis=1)

        fig = px.line(
            full, x="날짜", y="인원수(명)",
            markers=True, title="📈 서버 인원수 성장 추이"
        )
        fig.update_layout(font=dict(family="Malgun Gothic"))
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# 2️⃣ 활동 내역 (카드)
# ===============================
elif menu == "활동 내역":
    df = load_activity()
    if df is not None:
        summary = df.groupby(["이름", "종류"])["경험치"].sum().reset_index()
        top = summary.sort_values("경험치", ascending=False).groupby("종류").head(1)

        st.subheader("🏆 종류별 1위")
        cols = st.columns(len(top))
        for col, (_, row) in zip(cols, top.iterrows()):
            with col:
                st.markdown(f"""
                <div class="card">
                    <h3>{row['종류']} 1위</h3>
                    <p><b>{row['이름']}</b></p>
                    <p>경험치 {row['경험치']}</p>
                </div>
                """, unsafe_allow_html=True)

# ===============================
# 3️⃣ 관리진 목록 (카드)
# ===============================
elif menu == "관리진 목록":
    df = load_admin()
    if df is not None:
        st.subheader("🛡️ 현재 관리진")
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card">
                    <h3>{row['이름']}</h3>
                    <p>부서: {row['부서']}</p>
                    <p>직급: {row['직급']}</p>
                </div>
                """, unsafe_allow_html=True)

# ===============================
# 4️⃣ 이벤트 내역 (카드)
# ===============================
elif menu == "이벤트 내역":
    df = load_event()
    if df is not None:
        st.subheader("🎉 진행 이벤트")
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
                <h3>{row['이벤트 이름']}</h3>
                <p>운영 기간: {row['운영기간']}</p>
            </div>
            """, unsafe_allow_html=True)

# ===============================
# 5️⃣ 내전 로그 (상세 카드)
# ===============================
elif menu == "내전 로그":
    df = load_match()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])
        st.subheader("⚔️ 내전 기록")

        for _, row in df.iterrows():
            color = "#ef4444" if row["승리팀"] == "레드" else "#3b82f6"
            st.markdown(f"""
            <div class="card" style="border-left:6px solid {color};">
                <h3>{row['날짜'].strftime('%Y.%m.%d')} · {row['게임']}</h3>
                <p>참여 인원: {row['참여인원']}명</p>
                <p>🏆 승리 팀: <b style="color:{color}">{row['승리팀']}</b></p>
            </div>
            """, unsafe_allow_html=True)
