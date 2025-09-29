import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="MBTI by Asian Country — Compare with South Korea",
    page_icon="🇰🇷",
    layout="wide"
)

# ===== 헤더 이미지(선택) =====
for cand in ["header.png", "header.jpg", "banner.png", "banner.jpg"]:
    if Path(cand).exists():
        st.image(cand, use_column_width=True)
        break

# ===== 제목/설명 =====
st.title("🌏 아시아 국가 선택 → South Korea와 MBTI 분포 비교")
st.caption("같은 폴더의 `countriesMBTI_16types.csv`를 사용합니다. 아시아 국가를 선택하면 항상 South Korea와 함께 비교 차트가 즉시 갱신됩니다.")

# ===== 데이터 로드 =====
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    # 표기 정규화: 표시용 국가명으로 치환
    name_map = {
        "Korea, Republic of": "South Korea",
        "Korea, Democratic People's Republic of": "North Korea",
    }
    df["Country"] = df["Country"].replace(name_map)
    return df

df = load_data()
mbti_cols = [c for c in df.columns if c != "Country"]

# ===== 아시아 국가 목록(데이터셋과 교집합 사용) =====
asia_canon = {
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan",
    "Brunei Darussalam", "Cambodia", "China", "Georgia", "India", "Indonesia",
    "Iran (Islamic Republic of)", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan",
    "North Korea", "South Korea", "Kuwait", "Kyrgyzstan",
    "Lao People's Democratic Republic", "Lebanon", "Malaysia", "Maldives",
    "Mongolia", "Myanmar", "Nepal", "Oman", "Pakistan", "Philippines",
    "Qatar", "Saudi Arabia", "Singapore", "Sri Lanka", "State of Palestine",
    "Syrian Arab Republic", "Tajikistan", "Thailand", "Timor-Leste", "Türkiye",
    "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Viet Nam", "Yemen",
    "Hong Kong", "Macao", "Taiwan, Province of China", "Taiwan"
}
asia_list = sorted(set(df["Country"]).intersection(asia_canon))

# South Korea 존재 확인
if "South Korea" not in asia_list:
    st.error("데이터셋에 'South Korea'가 없습니다. CSV의 국가 표기를 확인해주세요.")
    st.stop()

# ===== 사이드바(선택 즉시 비교 차트 반영) =====
with st.sidebar:
    st.header("⚙️ 설정")
    st.markdown("**South Korea는 항상 기본 포함**됩니다.")

    compare_candidates = [c for c in asia_list if c != "South Korea"]
    # 예시 기본 선택
    default_sel = [c for c in ["Japan", "China"] if c in compare_candidates]

    selected_countries = st.multiselect(
        "비교할 아시아 국가 선택",
        options=compare_candidates,
        default=default_sel,
        help="선택/해제 시 곧바로 비교 차트에 반영됩니다."
    )

    top_n = st.slider(
        "상위 N 유형만 보기 (정렬 기준: South Korea 비율)",
        min_value=5, max_value=16, value=16, step=1
    )
    show_table = st.checkbox("비교 데이터 표로도 보기", value=False)

# ===== 항상 South Korea + 선택국들로 비교 세트 구성 =====
countries_to_plot = ["South Korea"] + [c for c in selected_countries if c != "South Korea"]

# ===== South Korea 기준 상위 N MBTI 선정 =====
kr_row = df[df["Country"] == "South Korea"].iloc[0]
kr_rank = pd.Series({m: kr_row[m] for m in mbti_cols}).sort_values(ascending=False)
top_mbti = kr_rank.head(top_n).index.tolist()

# ===== 롱포맷 데이터 생성 =====
records = []
for ctry in countries_to_plot:
    sub = df[df["Country"] == ctry].iloc[0]
    for m in top_mbti:
        records.append({
            "Country": ctry,
            "MBTI": m,
            "Ratio": float(sub[m]),
            "Percent": round(float(sub[m]) * 100, 2)
        })
long_df = pd.DataFrame(records)

# ===== 색상 매핑: South Korea 고정 파랑 + 나머지 팔레트 =====
def build_color_map(countries):
    base_cols = px.colors.qualitative.Safe + px.colors.qualitative.Set1 + px.colors.qualitative.Set3
    cmap = {"South Korea": "#1f77b4"}  # 선명한 파랑
    idx = 0
    for c in countries:
        if c == "South Korea":
            continue
        cmap[c] = base_cols[idx % len(base_cols)]
        idx += 1
    return cmap

color_map = build_color_map(countries_to_plot)

# ===== 비교 차트(그룹형 가로막대) =====
fig = px.bar(
    long_df,
    x="Percent",
    y="MBTI",
    color="Country",
    barmode="group",
    category_orders={"MBTI": top_mbti[::-1]},  # y축을 상위→하위로 위에서 아래로 보이도록
    color_discrete_map=color_map,
    hover_data={"Country": True, "MBTI": True, "Percent": True, "Ratio": False},
    template="simple_white",
)

fig.update_traces(texttemplate="%{x:.2f}%", textposition="outside", cliponaxis=False)
fig.update_layout(
    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형 (South Korea 비율 기준 상위 N)",
    margin=dict(l=10, r=10, t=10, b=10),
    bargap=0.18,
    bargroupgap=0.05,
    height=640,
    legend_title_text="국가",
)

# x축 상단 여유 확보
xmax = long_df["Percent"].max() if not long_df.empty else 0
fig.update_xaxes(range=[0, max(10, xmax * 1.25)])

# ===== 본문 출력 =====
st.subheader(f"🇰🇷 South Korea와 비교 (상위 {top_n}개 유형)")
st.plotly_chart(fig, use_container_width=True)

# 요약/표시
with st.expander("요약 보기"):
    st.markdown(
        f"- 포함 국가 수: **{len(countries_to_plot)}개**  \n"
        f"- MBTI 유형 표시: **상위 {top_n}개 (South Korea 기준)**"
    )

if show_table:
    st.markdown("### 📄 비교 데이터 표")
    st.dataframe(
        long_df.rename(columns={"Percent": "Percent (%)"}),
        use_container_width=True
    )

st.markdown("---")
st.caption("💡 상단에 `header.png`나 `header.jpg`를 두면 배너가 자동으로 표시됩니다.")
