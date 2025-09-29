import streamlit as st
import pandas as pd
import altair as alt

# 제목
st.title("🌍 MBTI 유형별 상위 10개 평균 비율")

# 데이터 불러오기
df = pd.read_csv("countriesMBTI_16types.csv")

# MBTI 컬럼만 추출 (Country 제외)
mbti_cols = df.columns[1:]

# 각 MBTI 유형의 평균 비율 계산
mbti_means = df[mbti_cols].mean().sort_values(ascending=False).head(10).reset_index()
mbti_means.columns = ["MBTI", "Average"]

# Altair 막대 그래프
chart = (
    alt.Chart(mbti_means)
    .mark_bar(color="skyblue")
    .encode(
        x=alt.X("Average:Q", title="평균 비율"),
        y=alt.Y("MBTI:N", sort="-x", title="MBTI 유형"),
        tooltip=["MBTI", "Average"]
    )
)

# 화면에 출력
st.altair_chart(chart, use_container_width=True)
