import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata
import io
import plotly.express as px
import plotly.graph_objects as go

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="2025 별빛카페 연말정산",
    layout="wide"
)

# ===============================
# 글로벌 스타일 (깔롱 핵심)
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}

.big-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0.2em;
}

.sub-title {
    color: #6b7280;
    font-size: 18px;
    margin-bottom: 2em;
}

.card {
    padding: 1.2em;
    border-radius: 18px;
    background: linear-gradient(135deg, #1f2937, #111827);
    color: white;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}

.metric-big {
    font-size: 28px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

# ===============================
# CSV 로더 (NFC/NFD 대응)
# ===============================
def load_csv_by_normalized_name(target_name: str):
    target_nfc = unicodedata.normalize("NFC", target_name)
    target_nfd = unicodedata.normalize("NFD", target_name)

    for file in DATA_DIR.iterdir():
        if not file.is_file():
            continue
        fname_nfc = unicodedata.normalize("NFC", file.name)
        fname_nfd = unicodedata.normalize("NFD", file.name)

        if fname_nfc == target_nfc or fname_nfd == target_nfd:
            return pd.read_csv(file)

    st.error(f"❌ 파일을 찾을 수 없습니다: {target_name}")
    return None

@st.cache_data
def load_member_data():
    return load_csv_by_normalized_name("별빛카페_인원수_변화.csv")

@st.cache_data
def load_activity_data():
    return load_csv_by_normalized_name("별빛카페_채팅음성.csv")

@st.cache_data
def load_admin_data():
    return load_csv_by_normalized_name("현재_관리자.csv")

@st.cache_data
def load_event_data():
    return load_csv_by_normalized_name("별빛카페_이벤트.csv")

@st.cache_data
def load_match_data():
    return load_csv_by_normalized_name("별빛카페_내전.csv")

# ===============================
# 제목
# ===============================
st.markdown('<div class="big-title">🌌 2025 별빛카페 연말정산</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">한 해 동안의 성장, 활동, 그리고 승부의 기록</div>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "📂 메뉴",
    ["인원수 변화", "활동 내역", "관리진 목록", "이벤트 내역", "내전 로그"]
)

# ===============================
# TAB 1 : 인원수 변화 (쌈뽕 버전)
# ===============================
if menu == "인원수 변화":
    df = load_member_data()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])
        df = df.sort_values("날짜")

        START = pd.to_datetime("2025-08-27")
        END = pd.to_datetime("2025-12-24")
        DAILY_INC = 6.51

        full_dates = pd.date_range(START, END, freq="D")
        full = pd.DataFrame({"날짜": full_dates})
        full = full.merge(df, on="날짜", how="left")

        base_date = df.iloc[0]["날짜"]
        base_val = df.iloc[0]["인원수(명)"]

        def estimate(row):
            if not pd.isna(row["인원수(명)"]):
                return row["인원수(명)"]
            return round(base_val + (row["날짜"] - base_date).days * DAILY_INC, 1)

        full["인원수(명)"] = full.apply(estimate, axis=1)
        full["일일증가"] = full["인원수(명)"].diff()

        col1, col2 = st.columns([3, 1])

        with col1:
            fig = px.line(
                full,
                x="날짜",
                y="인원수(명)",
                markers=True,
                title="📈 서버 인원수 성장 곡선"
            )
            fig.update_layout(
                font=dict(family="Malgun Gothic"),
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                title_font_size=22,
                title_font_color="white",
                xaxis=dict(gridcolor="#334155"),
                yaxis=dict(gridcolor="#334155"),
            )
            fig.update_traces(line=dict(width=4))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            avg = full["일일증가"].mean()
            st.markdown(f"""
            <div class="card">
                <div>📊 평균 일일 증가</div>
                <div class="metric-big">+{avg:.2f} 명</div>
                <div style="color:#9ca3af;margin-top:0.5em;">
                오픈 이후 꾸준한 성장
                </div>
            </div>
            """, unsafe_allow_html=True)

        buffer = io.BytesIO()
        full.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="📥 일별 인원수 추정 데이터 다운로드",
            data=buffer.getvalue(),
            file_name="별빛카페_인원수_일별_추정.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ===============================
# TAB 5 : 내전 로그 (요청 핵심!)
# ===============================
elif menu == "내전 로그":
    df = load_match_data()
    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])
        df = df.sort_values("날짜")

        st.subheader("⚔️ 내전 경기 기록")

        # 설명형 로그 생성
        df["경기 요약"] = (
            df["날짜"].dt.strftime("%Y-%m-%d") + " | "
            + df["게임"] + " | 승리 팀: "
            + df["승리팀"]
        )

        for _, row in df.iterrows():
            winner_color = "#ef4444" if row["승리팀"] == "레드" else "#3b82f6"
            st.markdown(f"""
            <div style="
                padding:1em;
                border-radius:14px;
                margin-bottom:0.6em;
                background:#020617;
                border-left:6px solid {winner_color};
            ">
                <b>{row['날짜'].strftime('%Y.%m.%d')}</b>  
                <br>🎮 게임: <b>{row['게임']}</b>  
                <br>👥 참여 인원: {row['참여인원']}명  
                <br>🏆 승리 팀: <span style="color:{winner_color};font-weight:700;">
                    {row['승리팀']}
                </span>
            </div>
            """, unsafe_allow_html=True)

        win_rate = df["승리팀"].value_counts(normalize=True) * 100

        fig = px.pie(
            values=win_rate.values,
            names=win_rate.index,
            title="팀별 승률"
        )
        fig.update_layout(
            font=dict(family="Malgun Gothic"),
            title_font_size=22
        )
        st.plotly_chart(fig, use_container_width=True)
