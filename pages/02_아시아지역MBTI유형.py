import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MBTI by Asian Country", page_icon="🌏", layout="wide")

# ===== 헤더 이미지 (있으면 자동 표시) =====
header_path = None
for cand in ["header.png", "header.jpg", "banner.png", "banner.jpg"]:
    if Path(cand).exists():
        header_path = cand
        break
if header_path:
    st.image(header_path, use_column_width=True)

# ===== 제목/설명 =====
st.title("🌏 아시아 국가 선택 → MBTI 16유형 비율")
st.caption("같은 폴더의 `countriesMBTI_16types.csv`를 사용합니다. 아시아 지역의 나라를 골라 해당 국가의 MBTI 분포를 확인해요.")

# ===== 데이터 로드 (캐시) =====
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("countriesMBTI_16types.csv")

df = load_data()

# ===== MBTI 컬럼 정의 =====
mbti_cols = [c for c in df.columns if c != "Country"]

# ===== 아시아 국가 목록 (UN 표기 기반, 데이터셋과 교집합만 사용) =====
asia_canon = {
    # 서아시아/중앙아시아/남아시아/동아시아/동남아시아
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan",
    "Brunei Darussalam", "Cambodia", "China", "Georgia", "India", "Indonesia",
    "Iran (Islamic Republic of)", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan",
    "Korea, Democratic People's Republic of", "Korea, Republic of", "Kuwait",
    "Kyrgyzstan", "Lao People's Democratic Republic", "Lebanon", "Malaysia",
    "Maldives", "Mongolia", "Myanmar", "Nepal", "Oman", "Pakistan", "Philippines",
    "Qatar", "Saudi Arabia", "Singapore", "Sri Lanka", "State of Palestine",
    "Syrian Arab Republic", "Tajikistan", "Thailand", "Timor-Leste", "Türkiye",
    "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Viet Nam", "Yemen",
    # 특별행정구/지역 (데이터셋에 있을 수도)
    "Hong Kong", "Macao", "Taiwan, Province of China", "Taiwan"
}

available_countries = sorted(set(df["Country"]).intersection(asia_canon))
if not available_countries:
    st.error("아시아 지역으로 분류된 국가가 데이터셋에서 발견되지 않았습니다. CSV의 국가 표기를 확인해주세요.")
    st.stop()

# ===== 사이드바: 국가 선택 및 옵션 =====
with st.sidebar:
    st.header("⚙️ 설정")
    default_ix = available_countries.index("Korea, Republic of") if "Korea, Republic of" in available_countries else 0
    country = st.selectbox("아시아 국가 선택", available_countries, index=default_ix)
    show_table = st.checkbox("원자료 표로도 보기", value=False)
    top_n = st.slider("상위 N개만 보기 (비율 내림차순)", min_value=5, max_value=16, value=16, step=1)
    st.markdown("---")
    st.caption("💡 팁: 상단에 `header.png`를 넣으면 예쁜 배너가 보여요!")

# ===== 선택 국가 데이터 가공 =====
row = df[df["Country"] == country].iloc[0]
data = (
    pd.DataFrame({"MBTI": mbti_cols, "Ratio": [row[c] for c in mbti_cols]})
    .sort_values("Ratio", ascending=False)
    .head(top_n)
    .reset_index(drop=True)
)
data["Percent"] = (data["Ratio"] * 100).round(2)

# ===== Plotly 색상 팔레트 (파스텔 + Set3 계열 믹스) =====
palette = (
    px.colors.qualitative.Set3
    + px.colors.qualitative.Pastel
    + px.colors.qualitative.Antique
)
colors = [palette[i % len(palette)] for i in range(len(data))]

# ===== 막대 그래프 =====
fig = px.bar(
    data,
    x="Percent",
    y="MBTI",
    orientation="h",
    text="Percent",
    color="MBTI",
    color_discrete_sequence=colors,
    hover_data={"MBTI": True, "Percent": True, "Ratio": False},
    title=None,
    template="simple_white",
)
fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False
)
fig.update_layout(
    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형",
    yaxis={"categoryorder": "total ascending"},
    margin=dict(l=10, r=10, t=10, b=10),
    legend_title_text="유형",
    bargap=0.25,
    height=620,
)

# x축 여유 공간
max_pct = data["Percent"].max() if len(data) else 0
fig.update_xaxes(range=[0, max(10, max_pct * 1.15)])

# ===== 출력 =====
left, right = st.columns([2, 1], gap="large")
with lef
