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
# 폰트 (가독성 중심)
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
.soft-card {
    background:#f9fafb;
    padding:1.2em;
    border-radius:14px;
    border:1px solid #e5e7eb;
    margin-bottom:1em;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

# ===============================
# CSV 로더 (NFC/NFD)
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
st.caption("한 해 동안의 성장, 활동, 그리고 승부의 기록")

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

        start, end = pd.to_datetime("2025-08-27"), pd.to_datetime("2025-12-24")
        daily = 6.51

        dates = pd.date_range(start, end, freq="D")
        full = pd.DataFrame({"날짜": dates}).merge(df, on="날짜", how="left")

        base_d, base_v = df.iloc[0]["날짜"], df.iloc[0]["인원수(명)"]

        full["인원수(명)"] = full.apply(
            lambda r: r["인원수(명)"] if pd.notna(r["인원수(명)"])
            else round(base_v + (r["날짜"] - base_d).days * daily, 1),
            axis=1
        )

        fig = px.line(
            full,
            x="날짜",
            y="인원수(명)",
            markers=True,
            title="📈 서버 인원수 변화 (일 평균 +6.51명 반영)"
        )
        fig.update_layout(font=dict(family="Malgun Gothic"))
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# 2️⃣ 활동 내역 (그래프 복구!)
# ===============================
elif menu == "활동 내역":
    df = activity()
    if df is not None:
        summary = df.groupby(["이름", "종류"])["경험치"].sum().reset_index()

        st.subheader("📊 채팅 · 음성 경험치 총합")

        fig = px.bar(
            summary,
            x="이름",
            y="경험치",
            color="종류",
            barmode="group"
        )
        fig.update_layout(
            font=dict(family="Malgun Gothic"),
            xaxis_title="유저",
            yaxis_title="경험치"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🏆 종류별 1위")
        top = summary.sort_values("경험치", ascending=False).groupby("종류").head(1)
        st.dataframe(top, use_container_width=True)

# ===============================
# 3️⃣ 관리진 목록 (심플 카드)
# ===============================
elif menu == "관리진 목록":
    df = admin()
    if df is not None:
        st.subheader("🛡️ 현재 관리진")
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
        st.subheader("🎉 진행 이벤트")
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="soft-card">
                <b>{r['이벤트 이름']}</b><br>
                운영 기간: {r['운영기간']}
            </div>
            """, unsafe_allow_html=True)

# ===============================
# 5️⃣ 내전 로그 (유지 + 승률 추가)
# ===============================
elif menu == "내전 로그":
    df = match()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])
        st.subheader("⚔️ 내전 기록")

        for _, r in df.iterrows():
            color = "#ef4444" if r["승리팀"] == "레드" else "#3b82f6"
            st.markdown(f"""
            <div class="soft-card" style="border-left:5px solid {color}">
                <b>{r['날짜'].strftime('%Y.%m.%d')} · {r['게임']}</b><br>
                참여 인원: {r['참여인원']}명<br>
                승리 팀: <b style="color:{color}">{r['승리팀']}</b>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("📊 팀별 승률")
        win_rate = df["승리팀"].value_counts(normalize=True) * 100
        fig = px.pie(
            values=win_rate.values,
            names=win_rate.index
        )
        fig.update_layout(font=dict(family="Malgun Gothic"))
        st.plotly_chart(fig, use_container_width=True)
