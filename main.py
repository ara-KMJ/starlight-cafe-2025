import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata
import io
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ===============================
# 기본 설정
# ===============================
st.set_page_config(
    page_title="2025 별빛카페 연말정산",
    layout="wide"
)

# ===============================
# 한글 폰트 (Streamlit)
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR&display=swap');
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

# ===============================
# CSV 로더 (NFC / NFD 완전 대응)
# ===============================
def load_csv_by_normalized_name(target_name: str):
    if not DATA_DIR.exists():
        st.error("❌ data 폴더가 존재하지 않습니다.")
        return None

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

# ===============================
# 데이터 로딩 (캐시)
# ===============================
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
st.title("🌌 2025 별빛카페 연말정산")

# ===============================
# 사이드바
# ===============================
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["인원수 변화", "활동 내역", "관리진 목록", "이벤트 내역", "내전 로그"]
)

# ===============================
# TAB 1 : 인원수 변화
# ===============================
if menu == "인원수 변화":
    with st.spinner("📊 인원수 데이터를 분석 중입니다..."):
        df = load_member_data()

    if df is not None:
        df["날짜"] = pd.to_datetime(df["날짜"])

        start_date = pd.to_datetime("2025-08-27")
        end_date = pd.to_datetime("2025-12-24")

        full_range = pd.date_range(start_date, end_date, freq="D")
        df_full = pd.DataFrame({"날짜": full_range})
        df_full = df_full.merge(df, on="날짜", how="left")

        # 11월 1일 이전 평균값으로 예측
        avg_before_nov = (
            df_full[df_full["날짜"] < "2025-11-01"]["인원수(명)"]
            .mean()
        )
        df_full["인원수(명)"] = df_full["인원수(명)"].fillna(avg_before_nov)

        df_full["일일변화"] = df_full["인원수(명)"].diff()
        avg_change = df_full["일일변화"].mean()

        fig = px.line(
            df_full,
            x="날짜",
            y="인원수(명)",
            title="📈 서버 인원수 변화"
        )
        fig.update_layout(
            font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.metric(
            label="평균 일일 인원 변화",
            value=f"{avg_change:.2f} 명",
            delta="상승" if avg_change > 0 else "하락"
        )

        # ===============================
        # XLSX 다운로드 (TypeError 방지)
        # ===============================
        buffer = io.BytesIO()
        df_full.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="📥 인원수 예측 결과 다운로드",
            data=buffer.getvalue(),
            file_name="인원수_예측_결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ===============================
# TAB 2 : 활동 내역
# ===============================
elif menu == "활동 내역":
    with st.spinner("💬 채팅 · 음성 활동을 집계 중입니다..."):
        df = load_activity_data()

    if df is not None:
        summary = (
            df.groupby(["이름", "종류"])["경험치"]
            .sum()
            .reset_index()
        )

        st.subheader("🏆 종류별 경험치 1위")
        top_users = (
            summary.sort_values("경험치", ascending=False)
            .groupby("종류")
            .head(1)
        )
        st.dataframe(top_users, use_container_width=True)

        fig = px.bar(
            summary,
            x="이름",
            y="경험치",
            color="종류",
            title="채팅 · 음성 경험치 총합"
        )
        fig.update_layout(
            font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# TAB 3 : 관리진 목록
# ===============================
elif menu == "관리진 목록":
    with st.spinner("🛡️ 관리진 목록을 불러오는 중입니다..."):
        df = load_admin_data()

    if df is not None:
        st.subheader("현재 관리진")
        st.dataframe(df, use_container_width=True)

# ===============================
# TAB 4 : 이벤트 내역
# ===============================
elif menu == "이벤트 내역":
    with st.spinner("🎉 이벤트 정보를 불러오는 중입니다..."):
        df = load_event_data()

    if df is not None:
        st.subheader("진행된 이벤트")
        st.dataframe(df, use_container_width=True)

# ===============================
# TAB 5 : 내전 로그
# ===============================
elif menu == "내전 로그":
    with st.spinner("⚔️ 내전 승률을 분석 중입니다..."):
        df = load_match_data()

    if df is not None:
        win_rate = df["승리팀"].value_counts(normalize=True) * 100

        st.subheader("팀별 승률 (%)")
        st.dataframe(win_rate.rename("승률(%)"))

        fig = px.pie(
            values=win_rate.values,
            names=win_rate.index,
            title="레드 팀 vs 블루 팀 승률"
        )
        fig.update_layout(
            font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)
