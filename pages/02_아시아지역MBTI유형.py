import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MBTI by Asian Country (with Korea comparison)", page_icon="🇰🇷", layout="wide")

# ============== 헤더 이미지 (있으면 자동 표시) ==============
header_path = None
for cand in ["header.png", "header.jpg", "banner.png", "banner.jpg"]:
    if Path(cand).exists():
        header_path = cand
        break
if header_path:
    st.image(header_path, use_column_width=True)

# ============== 제목/설명 ==============
st.title("🌏 아시아 국가 선택 → 한국과 MBTI 분포 비교")
st.caption("같은 폴더의 `countriesMBTI_16types.csv`를 사용합니다. 한국(Korea, Republic of)을 기준으로 다른 아시아 국가의 MBTI 16유형 분포를 비교해보세요.")

# ============== 데이터 로드 (캐시) ==============
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("countriesMBTI_16types.csv")

df = load_data()

# ============== MBTI 컬럼 정의 ==============
mbti_cols = [c for c in df.columns if c != "Country"]

# ============== 아시아 국가 목록 (데이터셋과 교집합만 사용) ==============
asia_canon = {
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan",
    "Brunei Darussalam", "Cambodia", "China", "Georgia", "India", "Indonesia",
    "Iran (Islamic Republic of)", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan",
    "Korea, Democratic People's Republic of", "Korea, Republic of", "Kuwait",
    "Kyrgyzstan", "Lao People's Democratic Republic", "Lebanon", "Malaysia",
    "Maldives", "Mongolia", "Myanmar", "Nepal", "Oman", "Pakistan", "Philippines",
    "Qatar", "Saudi Arabia", "Singapore", "Sri Lanka", "State of Palestine",
    "Syrian Arab Republic", "Tajikistan", "Thailand", "Timor-Leste", "Türkiye",
    "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Viet Nam", "Yemen",
    "Hong Kong", "Macao", "Taiwan, Province of China", "Taiwan"
}
asia_list = sorted(set(df["Country"]).intersection(asia_canon))

if "Korea, Republic of" not in asia_list:
    st.error("데이터셋에 'Korea, Republic of'가 없습니다. CSV의 국가 표기를 확인해주세요.")
    st.stop()

# ============== 사이드바 설정 ==============
with st.sidebar:
    st.header("⚙️ 설정")
    # 단일 국가 상세 보기(한국 포함 아시아 국가 중 선택)
    country_default_ix = asia_list.index("Korea, Republic of")
    country_single = st.selectbox("단일 국가 상세 보기", asia_list, index=country_default_ix)

    st.markdown("---")
    st.subheader("📊 한국과 비교(멀티 셀렉트)")
    # 한국을 제외한 리스트에서 선택
    compare_candidates = [c for c in asia_list if c != "Korea, Republic of"]
    preselect = []
    if "Japan" in compare_candidates: preselect.append("Japan")
    if "China" in compare_candidates: preselect.append("China")
    country_multi = st.multiselect(
        "비교할 아시아 국가 선택 (한국은 자동 포함)",
        compare_candidates,
        default=preselect
    )
    # 막대 개수(상위 N, 한국 기준)
    top_n = st.slider("상위 N개 유형만 보기 (정렬 기준: 한국 비율)", min_value=5, max_value=16, value=16, step=1)
    show_table = st.checkbox("비교 데이터 표로도 보기", value=False)

    st.markdown("---")
    st.caption("💡 팁: 상단에 `header.png`를 넣으면 예쁜 배너가 보여요!")

# ============== 단일 국가 상세(막대 그래프) ==============
row_single = df[df["Country"] == country_single].iloc[0]
single_df = (
    pd.DataFrame({"MBTI": mbti_cols, "Ratio": [row_single[c] for c in mbti_cols]})
    .sort_values("Ratio", ascending=False)
    .reset_index(drop=True)
)
single_df["Percent"] = (single_df["Ratio"] * 100).round(2)

# 색상 팔레트 (부드러운 파스텔 + Set3 + Antique)
palette = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel + px.colors.qualitative.Antique
colors_single = [palette[i % len(palette)] for i in range(len(single_df))]

fig_single = px.bar(
    single_df,
    x="Percent",
    y="MBTI",
    orientation="h",
    text="Percent",
    color="MBTI",
    color_discrete_sequence=colors_single,
    hover_data={"MBTI": True, "Percent": True, "Ratio": False},
    title=None,
    template="simple_white",
)
fig_single.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
fig_single.update_layout(
    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형",
    yaxis={"categoryorder": "total ascending"},
    margin=dict(l=10, r=10, t=10, b=10),
    legend_title_text="유형",
    bargap=0.25,
    height=560,
)
fig_single.update_xaxes(range=[0, max(10, single_df["Percent"].max() * 1.15)])

# ============== 한국 기준 멀티 비교용 데이터 가공 ==============
# 항상 한국 포함
countries_to_plot = ["Korea, Republic of"] + [c for c in country_multi if c != "Korea, Republic of"]

# 한국의 비율로 MBTI 정렬 기준 생성
kr_row = df[df["Country"] == "Korea, Republic of"].iloc[0]
kr_base = pd.Series({m: kr_row[m] for m in mbti_cols}).sort_values(ascending=False)
# 상위 N개만
kr_topN_mbti = kr_base.head(top_n).index.tolist()

# 롱포맷 변환
records = []
for ctry in countries_to_plot:
    sub = df[df["Country"] == ctry].iloc[0]
    for m in kr_topN_mbti:
        records.append({
            "Country": ctry,
            "MBTI": m,
            "Ratio": float(sub[m]),
            "Percent": round(float(sub[m]) * 100, 2)
        })
long_df = pd.DataFrame(records)

# MBTI 축 순서(한국 비율 내림차순) 유지
mbti_order = kr_topN_mbti

# 한국은 굵은 색, 비교국은 파스텔 위주 매핑
# 한국 색을 먼저 지정하고 나머지를 팔레트로 채움
def build_color_map(countries):
    base_cols = px.colors.qualitative.Safe + px.colors.qualitative.Set1 + px.colors.qualitative.Set3
    cmap = {}
    # 한국은 선명한 파랑 계열 지정
    cmap["Korea, Republic of"] = "#1f77b4"
    idx = 0
    for c in countries:
        if c == "Korea, Republic of":
            continue
        cmap[c] = base_cols[idx % len(base_cols)]
        idx += 1
    return cmap

country_color_map = build_color_map(countries_to_plot)

fig_cmp = px.bar(
    long_df,
    x="MBTI",
    y="Percent",
    color="Country",
    barmode="group",
    category_orders={"MBTI": mbti_order},
    color_discrete_map=country_color_map,
    hover_data={"Country": True, "MBTI": True, "Percent": True, "Ratio": False},
    template="simple_white",
)
fig_cmp.update_traces(texttemplate="%{y:.2f}%", textposition="outside", cliponaxis=False)
fig_cmp.update_layout(
    title=None,
    xaxis_title="MBTI 유형 (한국 비율 기준 상위 N)",
    yaxis_title="비율 (%)",
    margin=dict(l=10, r=10, t=10, b=10),
    bargap=0.18,
    bargroupgap=0.05,
    height=620,
    legend_title_text="국가",
)
# y축 상단 여유
ymax = long_df["Percent"].max() if not long_df.empty else 0
fig_cmp.update_yaxes(range=[0, max(10, ymax * 1.25)])

# ============== 출력 레이아웃 ==============
left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader(f"📈 단일 국가 상세: {country_single}")
    st.plotly_chart(fig_single, use_container_width=True)

with right:
    st.subheader("요약")
    if not single_df.empty:
        top1 = single_df.iloc[0]
        st.metric("가장 높은 유형", top1["MBTI"], f"{top1['Percent']:.2f}%")
    st.markdown(
        f"""
- 선택 국가(상세): **{country_single}**
- 비교 국가(한국 포함): **{len(countries_to_plot)}개**
- 상위 N(한국 기준): **{top_n}개 / 16개**
        """
    )
    st.caption("🧭 비교 차트의 MBTI 축은 **한국 비율 내림차순 Top N**으로 정렬됩니다.")

st.markdown("---")
st.subheader(f"🇰🇷 한국과 비교 (상위 {top_n}개 유형, 한국 기준 정렬)")
st.plotly_chart(fig_cmp, use_container_width=True)

if show_table:
    st.markdown("### 📄 비교 데이터 표")
    st.dataframe(
        long_df.rename(columns={"Percent": "Percent (%)"}),
        use_container_width=True
    )

st.markdown("---")
st.markdown("✅ Plotly로 상호작용, Streamlit Cloud에서 바로 동작합니다.  |  🖼 헤더 이미지는 선택사항입니다.")
