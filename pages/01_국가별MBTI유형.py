import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="MBTI by Country", page_icon="🌍", layout="wide")

# ===== 헤더 이미지 (있으면 표시) =====
header_path = None
for cand in ["header.png", "header.jpg", "banner.png", "banner.jpg"]:
    if Path(cand).exists():
        header_path = cand
        break
if header_path:
    st.image(header_path, use_column_width=True)

# ===== 제목 / 설명 =====
st.title("🌍 나라 선택 → MBTI 비율 보기")
st.caption("같은 폴더의 `countriesMBTI_16types.csv`를 사용합니다. 나라를 선택하면 해당 국가의 MBTI 16유형 분포를 보여줘요.")

# ===== 데이터 로드 =====
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# ===== 컬럼 정의 =====
mbti_cols = [c for c in df.columns if c != "Country"]

# ===== 사이드바 설정 =====
with st.sidebar:
    st.header("⚙️ 설정")
    countries = sorted(df["Country"].dropna().unique().tolist())
    default_ix = countries.index("Korea, Republic of") if "Korea, Republic of" in countries else 0
    country = st.selectbox("나라를 선택하세요", countries, index=default_ix)
    show_table = st.checkbox("원자료 표로도 보기", value=False)
    top_n = st.slider("상위 N개만 보기 (정렬 기준: 비율)", min_value=5, max_value=16, value=16, step=1)
    st.markdown("---")
    st.caption("💡 팁: 상위 N 슬라이더로 막대 수를 조정해보세요!")

# ===== 선택 국가 데이터 가공 =====
row = df[df["Country"] == country].iloc[0]
data = (
    pd.DataFrame({"MBTI": mbti_cols, "Ratio": [row[c] for c in mbti_cols]})
    .sort_values("Ratio", ascending=False)
    .head(top_n)
)

# 퍼센트 포맷 컬럼
data["Percent"] = (data["Ratio"] * 100).round(2)

# ===== Plotly 색상 팔레트 (부드럽고 선명한 톤) =====
# Set3 + Pastel 계열을 섞어 보기 좋게 길이 확장
palette = (
    px.colors.qualitative.Set3
    + px.colors.qualitative.Pastel
    + px.colors.qualitative.Antique
)
# 필요한 개수만큼 순환
colors = [palette[i % len(palette)] for i in range(len(data))]

# ===== 막대그래프 =====
fig = px.bar(
    data,
    x="Percent",
    y="MBTI",
    orientation="h",
    text="Percent",
    color="MBTI",
    color_discrete_sequence=colors,
    hover_data={"Ratio": False, "Percent": True, "MBTI": True},
)

# 레이아웃 미세 조정
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
    height=600,
)

# 값 범위 여유 공간
max_pct = data["Percent"].max() if len(data) else 0
fig.update_xaxes(range=[0, max(10, max_pct * 1.15)])

# ===== 출력 =====
left, right = st.columns([2, 1], gap="large")
with left:
    st.subheader(f"📈 {country} — MBTI 분포 (상위 {top_n}개)")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("요약")
    if not data.empty:
        top1 = data.iloc[0]
        st.metric("가장 높은 유형", f"{top1['MBTI']}", f"{top1['Percent']:.2f}%")
    st.markdown(
        f"""
- 선택한 국가: **{country}**
- 표시된 막대: **{len(data)}개**
- 전체 유형 수: **16개**
        """
    )
    st.markdown("—")
    st.caption("🧠 Tip: 헤더 이미지를 예쁘게 넣고 싶다면 같은 폴더에 `header.png`를 올려두세요!")

if show_table:
    st.markdown("### 📄 원자료 (선택국가)")
    st.dataframe(
        data[["MBTI", "Percent"]].rename(columns={"Percent": "Percent (%)"}),
        use_container_width=True
    )

# 깔끔한 풋터
st.markdown("---")
st.markdown("✅ Plotly로 상호작용, Streamlit Cloud에서 바로 동작합니다.  |  👀 이미지는 선택사항입니다.")
