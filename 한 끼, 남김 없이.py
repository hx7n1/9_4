
import streamlit as st
from datetime import date
import csv
import io

st.set_page_config(
    page_title="GREEN PLATE",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #F8FAF5;
}
header {
    visibility: visible;
}
.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}
.hero {
    background: linear-gradient(120deg, #DDEFD8, #EEF5E5);
    padding: 55px 35px;
    border-radius: 25px;
    text-align: center;
    color: #28543B;
    margin-bottom: 25px;
}
.hero h1 {
    font-size: 42px;
    font-weight: 900;
    color: #28543B;
}
.hero p {
    font-size: 18px;
    color: #52745C;
}
.section-title {
    color: #28543B;
    font-weight: 800;
    font-size: 25px;
    margin-top: 25px;
}
.card {
    background: white;
    border: 1px solid #E5EDE1;
    border-radius: 18px;
    padding: 23px;
    min-height: 175px;
    margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(50,80,50,0.04);
}
.card h3 {
    color: #315E40;
}
.card p {
    color: #68776A;
    font-size: 15px;
}
.icon {
    font-size: 35px;
}
.notice {
    background: #E9F2E5;
    border-radius: 18px;
    padding: 25px;
    color: #315E40;
    margin: 15px 0;
}
.small-text {
    color: #718071;
    font-size: 13px;
}
div.stButton > button {
    background-color: #477B51;
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #315E40;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# 상단 로고
st.markdown(
    "<h2 style='color:#315E40;'>🌱 GREEN PLATE "
    "<span style='font-size:14px;color:#839780;'> "
    "FOOD WASTE ZERO PROJECT</span></h2>",
    unsafe_allow_html=True
)

home_tab, analysis_tab = st.tabs([
    "🏡 HOME",
    "📊 잔반 분석하기"
])


# =========================
# HOME
# =========================

with home_tab:

    st.markdown("""
    <div class="hero">
        <div style="font-size:65px;">🌱 🍽️ 🌎</div>
        <h1>오늘의 한 끼가<br>지구의 내일을 바꿉니다.</h1>
        <p>
        무심코 남긴 반찬 하나가 환경에 부담이 될 수 있습니다.<br>
        GREEN PLATE와 함께 음식물 쓰레기를 줄여 보세요.
        </p>
        <div style="font-size:14px;font-weight:bold;">
        LESS FOOD WASTE · MORE GREEN EARTH
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>🌿 GREEN PLATE 소개</div>",
        unsafe_allow_html=True
    )

    st.write("""
    GREEN PLATE는 학교 급식에서 발생하는 음식물 쓰레기 문제를
    해결하기 위해 만들어진 환경 보호 프로젝트입니다.

    특히 모든 반찬이 똑같이 남는 것이 아니라 특정 반찬만
    반복적으로 남는 현상에 주목합니다.

    어떤 반찬이 많이 남는지 분석하고, 그 원인을 찾아
    잔반 처리 비용과 환경 부담을 줄이는 것이 우리의 목표입니다.
    """)

    st.markdown("""
    <div class="notice">
        <h3>💚 우리가 이 프로젝트를 만든 이유</h3>
        <p>
        맛이나 선호도에 따라 특정 반찬이 반복해서 남으면
        음식물 쓰레기가 증가합니다.<br>
        버려지는 음식은 처리 비용을 발생시키고 환경에도 부담을 줍니다.
        </p>
        <b>우리는 잔반을 단순히 버리는 문제가 아닌,
        개선할 수 있는 문제로 바라봅니다.</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>🔍 우리가 해결하려는 문제</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="card">
        <div class="icon">🥬</div>
        <h3>특정 반찬 잔반</h3>
        <p>학생들이 선호하지 않는 특정 반찬만 반복해서 남습니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card">
        <div class="icon">💸</div>
        <h3>처리 비용 증가</h3>
        <p>버려지는 음식이 많아질수록 잔반 처리에 드는 비용이 커집니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="card">
        <div class="icon">🌍</div>
        <h3>환경 부담 증가</h3>
        <p>음식물 쓰레기의 수거와 처리 과정에서 환경 부담이 발생합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>✨ GREEN PLATE의 주요 활동</div>",
        unsafe_allow_html=True
    )

    a, b = st.columns(2)

    with a:
        st.markdown("""
        <div class="card">
        <div class="icon">📊</div>
        <h3>01. 잔반 데이터 분석</h3>
        <p>반찬별 남은 양을 기록하고 가장 많이 남는 반찬을 찾아냅니다.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
        <div class="icon">💡</div>
        <h3>02. 맞춤형 해결 방법</h3>
        <p>배식량 조절과 조리법 개선 등 실천 가능한 방법을 제안합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown("""
        <div class="card">
        <div class="icon">💰</div>
        <h3>03. 처리 비용 계산</h3>
        <p>잔반량에 따른 예상 처리 비용을 계산합니다.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
        <div class="icon">🌱</div>
        <h3>04. 환경 보호 실천</h3>
        <p>잔반 감량 목표를 세우고 탄소 배출 추정 감소량을 확인합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>🌼 우리가 실천할 수 있는 작은 습관</div>",
        unsafe_allow_html=True
    )

    promises = [
        "먹을 수 있는 만큼만 배식받기",
        "처음에는 조금씩 받고 필요한 만큼 추가하기",
        "반찬을 남기는 이유 생각해 보기",
        "음식의 소중함을 친구들과 공유하기"
    ]

    for i, item in enumerate(promises):
        st.checkbox(item, key="promise_" + str(i))

    st.markdown("""
    <div class="notice" style="text-align:center;">
        <div style="font-size:45px;">🌎 💚 🌱</div>
        <h2>작은 실천이 모여 큰 변화를 만듭니다.</h2>
        <p>GREEN PLATE와 함께 음식물 쓰레기 줄이기에 참여해 보세요!</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "GREEN PLATE | 음식은 소중하게, 지구는 건강하게."
    )


# =========================
# ANALYSIS
# =========================

with analysis_tab:

    st.title("📊 반찬별 잔반 분석")
    st.write("급식에서 남은 반찬의 양을 입력해 보세요.")

    people = st.number_input(
        "급식 인원(명)", min_value=1, value=300
    )

    cost_rate = st.number_input(
        "잔반 처리 비용(원/kg)",
        min_value=0, value=500
    )

    co2_rate = st.number_input(
        "탄소 배출 추정치(kg CO2e/kg)",
        min_value=0.0, value=2.5, step=0.1
    )

    meal_date = st.date_input("급식 날짜", value=date.today())
    school = st.text_input("학교 이름 (선택)")

    st.subheader("반찬별 남은 양")

    names = []
    amounts = []

    default_names = [
        "김치", "시금치나물", "멸치볶음",
        "불고기", "기타"
    ]

    for i in range(5):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input(
                f"반찬 {i+1}",
                value=default_names[i],
                key=f"food_{i}"
            )

        with c2:
            amount = st.number_input(
                f"남은 양 {i+1} (kg)",
                min_value=0.0,
                max_value=100000.0,
                value=0.0,
                step=0.1,
                key=f"weight_{i}"
            )

        names.append(name.strip())
        amounts.append(amount)

    if st.button("잔반 분석 시작", use_container_width=True):

        totals = {}

        for name, amount in zip(names, amounts):
            if name and amount > 0:
                totals[name] = totals.get(name, 0.0) + amount

        total = sum(totals.values())

        st.subheader("분석 결과")

        x1, x2, x3, x4 = st.columns(4)

        x1.metric("총 잔반량", f"{total:.2f}kg")
        x2.metric(
            "1인당 잔반량",
            f"{total * 1000 / people:.1f}g"
        )
        x3.metric(
            "예상 처리 비용",
            f"{total * cost_rate:,.0f}원"
        )
        x4.metric(
            "탄소 배출 추정치",
            f"{total * co2_rate:.1f}kg"
        )

        if not totals:
            st.info("반찬별 잔반량을 입력해 주세요.")

        else:
            ordered = sorted(
                totals.items(),
                key=lambda x: x[1],
                reverse=True
            )

            st.subheader("반찬별 잔반 비교")

            for name, amount in ordered:
                ratio = amount / total
                st.write(
                    f"**{name}** : {amount:.2f}kg "
                    f"({ratio*100:.1f}%)"
                )
                st.progress(ratio)

            top_name, top_amount = ordered[0]

            st.warning(
                f"가장 많이 남은 반찬은 {top_name}입니다."
            )

            st.subheader("💡 개선 방법")

            st.markdown("""
            1. 처음 배식량을 조절하고 추가 배식을 허용합니다.
            2. 학생들의 반찬 선호도를 조사합니다.
            3. 반찬의 맛과 식감을 개선합니다.
            4. 잔반 기록을 비교해 적절한 조리량을 찾습니다.
            """)

            st.subheader("🌱 잔반 감량 목표")

            target = st.slider(
                "감량 목표 (%)", 5, 80, 20, 5
            )

            saved = total * target / 100

            st.write(f"예상 감량량: **{saved:.2f}kg**")
            st.write(
                f"예상 비용 절감: **{saved * cost_rate:,.0f}원**"
            )
            st.write(
                f"탄소 배출 추정 감소: "
                f"**{saved * co2_rate:.1f}kg CO2e**"
            )

            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow([
                "날짜", "학교", "반찬", "잔반량(kg)",
                "예상 처리 비용(원)"
            ])

            for name, amount in ordered:
                writer.writerow([
                    meal_date.isoformat(),
                    school,
                    name,
                    amount,
                    amount * cost_rate
                ])

            st.download_button(
                "📥 잔반 기록 다운로드",
                data="\ufeff" + output.getvalue(),
                file_name="GREEN_PLATE_잔반기록.csv",
                mime="text/csv"
            )

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#839780;'>"
    "🌱 GREEN PLATE | LESS WASTE, MORE GREEN"
    "</p>",
    unsafe_allow_html=True
)
