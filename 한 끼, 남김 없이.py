
import streamlit as st
from datetime import date
import csv
import io

st.set_page_config(
    page_title="잔반 줄이기",
    page_icon="🥗",
    layout="wide"
)

st.title("잔반 줄이기 실천 도우미")
st.write("반찬별 잔반을 분석하고 비용과 환경 부담을 줄여 보세요.")

st.sidebar.header("계산 기준")

people = st.sidebar.number_input(
    "급식 인원(명)", min_value=1, value=300
)
cost_rate = st.sidebar.number_input(
    "처리 비용(원/kg)", min_value=0, value=500
)
co2_rate = st.sidebar.number_input(
    "탄소 배출 추정치(kg CO2e/kg)",
    min_value=0.0, value=2.5, step=0.1
)

st.subheader("1. 급식 정보")
meal_date = st.date_input("날짜", value=date.today())
place = st.text_input("학교 이름(선택)")

st.subheader("2. 반찬별 잔반량")
st.caption("반찬 이름과 남은 양을 입력하세요.")

names = []
amounts = []

for i in range(5):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            f"반찬 이름 {i + 1}",
            value=["김치", "나물", "볶음 반찬", "메인 반찬", "기타"][i],
            key=f"name_{i}"
        )

    with col2:
        amount = st.number_input(
            f"남은 양 {i + 1} (kg)",
            min_value=0.0,
            max_value=100000.0,
            value=0.0,
            step=0.1,
            key=f"amount_{i}"
        )

    names.append(name.strip())
    amounts.append(float(amount))

if st.button("잔반 분석하기", use_container_width=True):
    totals = {}

    for name, amount in zip(names, amounts):
        if name and amount > 0:
            totals[name] = totals.get(name, 0.0) + amount

    total = sum(totals.values())

    st.subheader("3. 분석 결과")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("총 잔반량", f"{total:.2f} kg")
    col2.metric("1인당 잔반량", f"{total * 1000 / people:.1f} g")
    col3.metric("예상 처리 비용", f"{total * cost_rate:,.0f}원")
    col4.metric("탄소 배출 추정치", f"{total * co2_rate:.1f} kg")

    if not totals:
        st.info("반찬별 남은 양을 입력한 다음 다시 분석하세요.")

    else:
        ordered = sorted(
            totals.items(),
            key=lambda item: item[1],
            reverse=True
        )

        st.subheader("4. 반찬별 잔반 분석")

        for name, amount in ordered:
            share = amount / total
            st.write(
                f"**{name}**: {amount:.2f}kg "
                f"({share * 100:.1f}%)"
            )
            st.progress(share)

        top_name, top_amount = ordered[0]

        st.warning(
            f"가장 많이 남은 반찬: {top_name} "
            f"({top_amount:.2f}kg)"
        )

        st.subheader("5. 개선 방법")

        st.markdown("""
        - **배식량 조절:** 처음에는 적당량을 배식하고 추가 배식을 허용합니다.
        - **선호도 조사:** 학생들에게 맛, 간, 식감에 대한 의견을 물어봅니다.
        - **조리법 개선:** 잔반이 많은 반찬의 조리법을 점검합니다.
        - **조리량 조정:** 여러 날의 기록을 비교해 필요한 양을 계산합니다.
        """)

        st.subheader("6. 감량 목표")

        target = st.slider(
            "잔반 감량 목표(%)", 5, 80, 20, 5
        )

        saved = total * target / 100

        st.write(f"예상 감량량: **{saved:.2f}kg**")
        st.write(f"예상 비용 절감: **{saved * cost_rate:,.0f}원**")
        st.write(
            f"탄소 배출 추정 감소: "
            f"**{saved * co2_rate:.1f}kg CO2e**"
        )

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "날짜", "학교", "반찬 이름",
            "잔반량(kg)", "처리 비용(원)"
        ])

        for name, amount in ordered:
            writer.writerow([
                meal_date.isoformat(),
                place,
                name,
                round(amount, 2),
                round(amount * cost_rate)
            ])

        st.download_button(
            "잔반 기록 다운로드 (CSV)",
            data="\ufeff" + output.getvalue(),
            file_name="잔반기록.csv",
            mime="text/csv"
        )

st.caption(
    "비용과 탄소 배출량은 입력한 기준에 따른 추정치입니다."
)
