import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="숨은 한입 | 잔반 감축 연구소",
    page_icon="🥟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데모용 예시 데이터입니다. 실제 측정값이 아닙니다.
INITIAL_DATA = [
    {
        "날짜": "2026-10-26",
        "반찬": "당근볶음",
        "제공량(kg)": 8.0,
        "잔반량(kg)": 3.2,
        "조리법": "기본 제공",
        "메모": "식감 호불호",
    },
    {
        "날짜": "2026-10-26",
        "반찬": "버섯볶음",
        "제공량(kg)": 7.0,
        "잔반량(kg)": 2.1,
        "조리법": "기본 제공",
        "메모": "향에 대한 호불호",
    },
    {
        "날짜": "2026-10-26",
        "반찬": "시금치나물",
        "제공량(kg)": 6.0,
        "잔반량(kg)": 1.5,
        "조리법": "기본 제공",
        "메모": "질감 개선 필요",
    },
]

RECIPE_GUIDE = {
    "당근": {
        "제목": "🥟 당근 두부 만두소",
        "방법": [
            "당근을 깨끗이 씻어 잘게 다집니다.",
            "두부의 물기를 제거하고 으깬 뒤 당근과 섞습니다.",
            "기호에 따라 잘게 썬 양배추 등 다른 재료를 더하고 충분히 익힙니다.",
            "만두피에 넣어 속까지 완전히 익힙니다.",
        ],
        "팁": "당근의 단맛과 두부의 부드러운 식감을 활용합니다. 재료를 숨겨 알레르기 정보를 감추지 말고 메뉴에 표시하세요.",
    },
    "버섯": {
        "제목": "🥟 잘게 다진 버섯 만두",
        "방법": [
            "버섯을 깨끗이 손질하고 수분이 날아가도록 충분히 익힙니다.",
            "잘게 다진 버섯을 두부 또는 익힌 채소와 섞습니다.",
            "간은 싱겁게 조절하고 만두피에 소량씩 넣습니다.",
            "속까지 완전히 익힌 뒤 제공하고 식감 선호도를 확인합니다.",
        ],
        "팁": "버섯 향이 강하게 느껴지는 경우 다른 재료와 균형을 맞춰 소량부터 시험해 보세요.",
    },
    "시금치": {
        "제목": "🥬 시금치 채소전",
        "방법": [
            "시금치를 깨끗이 씻고 데친 뒤 물기를 짭니다.",
            "시금치를 잘게 썰어 반죽에 고르게 섞습니다.",
            "작은 크기로 부쳐 먹기 편하게 제공합니다.",
            "중심부까지 충분히 익었는지 확인합니다.",
        ],
        "팁": "한입 크기로 제공하면 낯선 식재료를 조금씩 맛볼 수 있습니다.",
    },
    "브로콜리": {
        "제목": "🍙 브로콜리 한입 주먹밥",
        "방법": [
            "브로콜리를 충분히 익힌 뒤 잘게 다집니다.",
            "밥과 다진 브로콜리를 고르게 섞습니다.",
            "소금은 적게 사용하고 작은 주먹밥으로 빚습니다.",
            "재료와 알레르기 정보를 표시해 제공합니다.",
        ],
        "팁": "채소가 밥에 고르게 섞여 한입씩 먹기 쉽습니다.",
    },
    "콩": {
        "제목": "🥟 부드러운 콩 채소 만두소",
        "방법": [
            "콩은 식품 종류에 맞게 충분히 익혀 준비합니다.",
            "익힌 콩을 으깨고 잘게 다진 채소와 섞습니다.",
            "수분을 조절해 만두소를 만들고 만두피에 넣습니다.",
            "속까지 완전히 익혀 제공하며 재료를 메뉴에 표시합니다.",
        ],
        "팁": "콩의 종류와 조리법에 맞는 안전한 가열 방법을 따르세요.",
    },
}

DEFAULT_RECIPE = {
    "제목": "🍳 잘게 다진 채소전",
    "방법": [
        "재료를 깨끗이 씻고 먹기 편한 크기로 잘게 다집니다.",
        "수분이 많은 재료는 적절히 제거하고 다른 재료와 섞습니다.",
        "작은 크기로 조리해 먹기 편하게 제공합니다.",
        "재료 특성에 맞게 속까지 충분히 익힙니다.",
    ],
    "팁": "새 조리법과 재료를 함께 안내하고 소량 시식으로 선호도를 확인하세요.",
}


def init_state():
    """세션 상태를 최초 한 번 초기화합니다."""
    if "records" not in st.session_state:
        st.session_state.records = pd.DataFrame(INITIAL_DATA)

    if "experiments" not in st.session_state:
        st.session_state.experiments = []


def safe_numeric(series):
    """숫자로 변환할 수 없는 값은 0으로 처리합니다."""
    return pd.to_numeric(series, errors="coerce").fillna(0)


def prepare_records(data):
    """데이터의 열과 숫자 형식을 검증합니다."""
    columns = [
        "날짜",
        "반찬",
        "제공량(kg)",
        "잔반량(kg)",
        "조리법",
        "메모",
    ]

    data = data.copy()

    for col in columns:
        if col not in data.columns:
            if col in ["제공량(kg)", "잔반량(kg)"]:
                data[col] = 0
            else:
                data[col] = ""

    data = data[columns].copy()

    data["제공량(kg)"] = safe_numeric(
        data["제공량(kg)"]
    ).clip(lower=0)

    data["잔반량(kg)"] = safe_numeric(
        data["잔반량(kg)"]
    ).clip(lower=0)

    for col in ["날짜", "반찬", "조리법", "메모"]:
        data[col] = data[col].fillna("").astype(str)

    # 잔반량은 제공량보다 클 수 없습니다.
    data["잔반량(kg)"] = data[
        ["잔반량(kg)", "제공량(kg)"]
    ].min(axis=1)

    return data


def waste_rate(row):
    """잔반율을 계산합니다."""
    served = float(row["제공량(kg)"])

    if served <= 0:
        return 0.0

    return float(row["잔반량(kg)"]) / served * 100


def recipe_for(name):
    """반찬 이름에 맞는 조리법을 찾습니다."""
    name = str(name).lower()

    for keyword, recipe in RECIPE_GUIDE.items():
        if keyword in name:
            return recipe

    return DEFAULT_RECIPE


init_state()

st.session_state.records = prepare_records(
    st.session_state.records
)

# 화면 스타일
st.markdown(
    """
    <style>
    .main {
        background: #fbfaf6;
    }

    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #e6f4e8, #fff0d9);
        border: 1px solid #d7e8d8;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        color: #244b36;
    }

    .hero p {
        margin: .45rem 0 0 0;
        color: #425448;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e8e6de;
        padding: 14px;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 사이드바
with st.sidebar:
    st.title("🥟 숨은 한입")
    st.caption("잔반 감축 연구소")

    page = st.radio(
        "메뉴",
        [
            "📊 잔반 대시보드",
            "🛟 반찬 구조대",
            "🥟 숨은 한입 레시피",
            "🌱 환경 효과 계산기",
            "📝 실험 기록장",
            "📁 데이터 관리",
        ],
    )

    st.divider()

    st.caption(
        "데모 데이터는 예시입니다. "
        "입력한 데이터는 현재 세션에서만 유지됩니다."
    )

st.markdown(
    """
    <div class="hero">
        <h1>숨은 한입</h1>
        <p>
            남김이 많은 반찬을 발견하고,
            먹기 편한 조리법을 실험해 음식물 쓰레기를 줄여요.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

df = prepare_records(st.session_state.records)

total_served = float(df["제공량(kg)"].sum())
total_waste = float(df["잔반량(kg)"].sum())

overall_rate = (
    total_waste / total_served * 100
    if total_served > 0
    else 0.0
)


# --------------------------------------------------
# 1. 잔반 대시보드
# --------------------------------------------------
if page == "📊 잔반 대시보드":

    st.subheader("잔반 현황 한눈에 보기")

    st.caption(
        "현재 기록된 데이터 전체를 보여줍니다. "
        "기본 데이터는 기능 확인용 예시입니다."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "누적 제공량",
        f"{total_served:,.1f} kg",
    )

    col2.metric(
        "누적 잔반량",
        f"{total_waste:,.1f} kg",
    )

    col3.metric(
        "전체 잔반율",
        f"{overall_rate:.1f}%",
    )

    st.divider()

    if df.empty:
        st.info(
            "아직 기록이 없습니다. "
            "데이터 관리 메뉴에서 잔반 기록을 추가해 주세요."
        )

    else:
        chart_df = df.copy()

        chart_df["잔반율(%)"] = chart_df.apply(
            waste_rate,
            axis=1,
        ).round(1)

        left, right = st.columns(2)

        with left:
            st.markdown("#### 반찬별 잔반량")

            waste_chart = chart_df.groupby(
                "반찬",
                as_index=True,
            )["잔반량(kg)"].sum()

            st.bar_chart(waste_chart)

        with right:
            st.markdown("#### 반찬별 잔반율")

            rate_summary = chart_df.groupby(
                "반찬",
                as_index=False,
            ).agg(
                제공량=("제공량(kg)", "sum"),
                잔반량=("잔반량(kg)", "sum"),
            )

            rate_summary["잔반율(%)"] = (
                rate_summary["잔반량"]
                / rate_summary["제공량"].replace(0, float("nan"))
                * 100
            ).fillna(0)

            st.bar_chart(
                rate_summary.set_index("반찬")[["잔반율(%)"]]
            )

        st.markdown("#### 기록 상세")

        st.dataframe(
            chart_df,
            use_container_width=True,
            hide_index=True,
        )

        summary = chart_df.groupby(
            "반찬",
            as_index=False,
        ).agg(
            제공량=("제공량(kg)", "sum"),
            잔반량=("잔반량(kg)", "sum"),
        )

        summary["잔반율(%)"] = (
            summary["잔반량"]
            / summary["제공량"].replace(0, float("nan"))
            * 100
        ).fillna(0)

        summary = summary.sort_values(
            "잔반율(%)",
            ascending=False,
        )

        if not summary.empty:
            worst = summary.iloc[0]

            st.success(
                f"우선 살펴볼 반찬: **{worst['반찬']}** "
                f"(잔반율 {worst['잔반율(%)']:.1f}%)"
            )


# --------------------------------------------------
# 2. 반찬 구조대
# --------------------------------------------------
elif page == "🛟 반찬 구조대":

    st.subheader("잔반이 많은 반찬부터 구조해요")

    st.write(
        "반찬별 잔반율과 잔반량을 비교해 "
        "개선 실험의 우선순위를 정합니다."
    )

    if df.empty:
        st.info("잔반 기록을 먼저 추가해 주세요.")

    else:
        summary = df.groupby(
            "반찬",
            as_index=False,
        ).agg(
            제공량=("제공량(kg)", "sum"),
            잔반량=("잔반량(kg)", "sum"),
            기록횟수=("날짜", "count"),
        )

        summary["잔반율(%)"] = (
            summary["잔반량"]
            / summary["제공량"].replace(0, float("nan"))
            * 100
        ).fillna(0)

        def priority(rate):
            if rate >= 40:
                return "높음"
            if rate >= 20:
                return "보통"
            return "관찰"

        summary["개선 우선순위"] = (
            summary["잔반율(%)"].apply(priority)
        )

        summary = summary.sort_values(
            ["잔반율(%)", "잔반량"],
            ascending=False,
        )

        st.dataframe(
            summary.style.format(
                {
                    "제공량": "{:.1f}",
                    "잔반량": "{:.1f}",
                    "잔반율(%)": "{:.1f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        selected = st.selectbox(
            "조리 방법을 검토할 반찬",
            summary["반찬"].tolist(),
        )

        recipe = recipe_for(selected)

        st.markdown(f"### {recipe['제목']}")
        st.caption(f"선택한 반찬: {selected}")

        for index, step in enumerate(
            recipe["방법"],
            start=1,
        ):
            st.write(f"**{index}.** {step}")

        st.info(recipe["팁"])

        st.warning(
            "재료를 다지거나 섞더라도 메뉴명, 원재료, "
            "알레르기 유발 식품은 정확하게 표시하세요."
        )


# --------------------------------------------------
# 3. 숨은 한입 레시피
# --------------------------------------------------
elif page == "🥟 숨은 한입 레시피":

    st.subheader("반찬을 먹기 편한 형태로 다시 설계해요")

    food = st.selectbox(
        "재료 또는 반찬 선택",
        [
            "당근",
            "버섯",
            "시금치",
            "브로콜리",
            "콩",
            "기타 채소",
        ],
    )

    recipe = RECIPE_GUIDE.get(
        food,
        DEFAULT_RECIPE,
    )

    st.markdown(f"## {recipe['제목']}")

    st.write("**조리 순서**")

    for index, step in enumerate(
        recipe["방법"],
        start=1,
    ):
        st.write(f"{index}. {step}")

    st.markdown("#### 작은 실험 제안")

    st.write(
        "- 한 번에 메뉴 전체를 바꾸기보다 소량 시식부터 시작합니다."
    )

    st.write(
        "- 조리법 변경 전후에 제공량과 잔반량을 같은 단위(kg)로 측정합니다."
    )

    st.write(
        "- 맛, 향, 식감 중 어떤 요소가 영향을 주었는지 "
        "짧은 설문으로 확인합니다."
    )

    st.info(recipe["팁"])

    with st.expander("급식 현장 안전 체크"):

        st.write(
            "- 식품 알레르기와 교차 접촉 가능성을 확인합니다."
        )

        st.write(
            "- 손 씻기, 조리 도구 세척, 적정 가열 및 보관 기준을 준수합니다."
        )

        st.write(
            "- 식재료가 보이지 않는 형태로 바뀌어도 "
            "원재료와 메뉴 정보를 공개합니다."
        )

        st.write(
            "- 학생이 먹지 않겠다는 선택을 할 수 있도록 안내합니다."
        )


# --------------------------------------------------
# 4. 환경 효과 계산기
# --------------------------------------------------
elif page == "🌱 환경 효과 계산기":

    st.subheader("잔반 감축 목표를 숫자로 바꿔봐요")

    st.caption(
        "비용과 환경 효과는 입력값을 이용한 추정치입니다. "
        "실제 청구액이나 공식 배출량 산정을 대신하지 않습니다."
    )

    left, right = st.columns(2)

    with left:

        current = st.number_input(
            "현재 하루 잔반량 (kg)",
            min_value=0.0,
            value=float(round(total_waste, 1)),
            step=0.5,
        )

        target_percent = st.slider(
            "잔반 감축 목표 (%)",
            min_value=0,
            max_value=80,
            value=20,
            step=5,
        )

        days = st.number_input(
            "운영 일수 (일)",
            min_value=1,
            max_value=366,
            value=200,
            step=10,
        )

    with right:

        cost_per_kg = st.number_input(
            "처리 비용 (원/kg)",
            min_value=0,
            value=150,
            step=10,
        )

        co2_per_kg = st.number_input(
            "가정한 배출계수 (kg CO₂e/kg 잔반)",
            min_value=0.0,
            value=0.5,
            step=0.1,
            format="%.2f",
        )

        st.caption(
            "배출계수 0.5는 계산 예시이며 "
            "실제 현장에서 검증된 값이 아닙니다."
        )

    reduced_daily = current * target_percent / 100
    reduced_total = reduced_daily * days
    saved_cost = reduced_total * cost_per_kg
    avoided_co2 = reduced_total * co2_per_kg

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "하루 감축 목표",
        f"{reduced_daily:.2f} kg",
    )

    col2.metric(
        "기간 내 감축 목표",
        f"{reduced_total:.1f} kg",
    )

    col3.metric(
        "예상 처리비 절감",
        f"{saved_cost:,.0f} 원",
    )

    st.metric(
        "가정한 배출계수 기준 예상 배출 감소",
        f"{avoided_co2:,.1f} kg CO₂e",
    )

    st.caption(
        "실제 결과는 잔반 처리 방식, 지역별 계약, "
        "음식물 구성 및 배출계수에 따라 달라집니다."
    )


# --------------------------------------------------
# 5. 실험 기록장
# --------------------------------------------------
elif page == "📝 실험 기록장":

    st.subheader("조리법을 바꾸고 결과를 기록해요")

    st.write(
        "기록은 현재 세션 동안 유지됩니다. "
        "장기 보관하려면 CSV로 내려받으세요."
    )

    with st.form(
        "experiment_form",
        clear_on_submit=True,
    ):

        exp_date = st.date_input(
            "실험 날짜",
            value=date.today(),
        )

        exp_food = st.text_input(
            "반찬 이름",
            placeholder="예: 당근볶음",
        )

        exp_method = st.selectbox(
            "시도한 조리법",
            [
                "잘게 다지기",
                "만두소로 활용",
                "전으로 만들기",
                "볶음밥에 섞기",
                "기타",
            ],
        )

        exp_before = st.number_input(
            "변경 전 잔반량 (kg)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )

        exp_after = st.number_input(
            "변경 후 잔반량 (kg)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )

        exp_note = st.text_area(
            "관찰 메모",
            placeholder="식감 반응, 시식 의견, 제공량 변화 등",
        )

        submitted = st.form_submit_button(
            "실험 기록 저장",
            type="primary",
        )

        if submitted:

            if not exp_food.strip():

                st.error("반찬 이름을 입력해 주세요.")

            else:

                improvement = (
                    (exp_before - exp_after)
                    / exp_before
                    * 100
                    if exp_before > 0
                    else None
                )

                record = {
                    "날짜": exp_date.isoformat(),
                    "반찬": exp_food.strip(),
                    "조리법": exp_method,
                    "변경 전 잔반량(kg)": round(
                        exp_before, 3
                    ),
                    "변경 후 잔반량(kg)": round(
                        exp_after, 3
                    ),
                    "잔반 변화율(%)": (
                        round(improvement, 1)
                        if improvement is not None
                        else None
                    ),
                    "메모": exp_note.strip(),
                }

                st.session_state.experiments.append(record)

                st.success("실험 기록을 저장했습니다.")

    if st.session_state.experiments:

        exp_df = pd.DataFrame(
            st.session_state.experiments
        )

        st.dataframe(
            exp_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "실험 기록 CSV 다운로드",
            data=exp_df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="hidden_bite_experiments.csv",
            mime="text/csv",
        )

        if st.button("실험 기록 모두 지우기"):

            st.session_state.experiments = []

            st.rerun()

    else:

        st.info(
            "아직 실험 기록이 없습니다. "
            "첫 조리 실험을 기록해 보세요."
        )


# --------------------------------------------------
# 6. 데이터 관리
# --------------------------------------------------
elif page == "📁 데이터 관리":

    st.subheader("잔반 기록 추가 또는 CSV 관리")

    with st.form(
        "record_form",
        clear_on_submit=True,
    ):

        record_date = st.date_input(
            "측정 날짜",
            value=date.today(),
        )

        record_food = st.text_input(
            "반찬 이름",
            placeholder="예: 당근볶음",
        )

        served = st.number_input(
            "제공량 (kg)",
            min_value=0.0,
            value=1.0,
            step=0.1,
        )

        waste = st.number_input(
            "잔반량 (kg)",
            min_value=0.0,
            value=0.2,
            step=0.1,
        )

        method = st.selectbox(
            "조리법",
            [
                "기본 제공",
                "잘게 다지기",
                "만두소로 활용",
                "전으로 만들기",
                "볶음밥에 섞기",
                "기타",
            ],
        )

        note = st.text_input("메모 (선택)")

        add_record = st.form_submit_button(
            "기록 추가",
            type="primary",
        )

        if add_record:

            if not record_food.strip():

                st.error("반찬 이름을 입력해 주세요.")

            elif waste > served:

                st.error(
                    "잔반량은 제공량보다 클 수 없습니다."
                )

            else:

                new_record = {
                    "날짜": record_date.isoformat(),
                    "반찬": record_food.strip(),
                    "제공량(kg)": float(served),
                    "잔반량(kg)": float(waste),
                    "조리법": method,
                    "메모": note.strip(),
                }

                st.session_state.records = pd.concat(
                    [
                        st.session_state.records,
                        pd.DataFrame([new_record]),
                    ],
                    ignore_index=True,
                )

                st.success("잔반 기록을 추가했습니다.")

                st.rerun()

    st.markdown("#### 현재 잔반 데이터")

    current_df = prepare_records(
        st.session_state.records
    )

    st.dataframe(
        current_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "현재 데이터 CSV 다운로드",
        data=current_df.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="hidden_bite_records.csv",
        mime="text/csv",
    )

    uploaded = st.file_uploader(
        "CSV 파일로 데이터 불러오기",
        type=["csv"],
    )

    if uploaded is not None:

        try:

            imported = pd.read_csv(uploaded)

            required = {
                "날짜",
                "반찬",
                "제공량(kg)",
                "잔반량(kg)",
            }

            if not required.issubset(
                set(imported.columns)
            ):

                st.error(
                    "CSV에 날짜, 반찬, 제공량(kg), "
                    "잔반량(kg) 열이 필요합니다."
                )

            else:

                imported = prepare_records(imported)

                st.dataframe(
                    imported.head(10),
                    use_container_width=True,
                    hide_index=True,
                )

                if st.button(
                    "불러온 CSV로 현재 데이터 교체"
                ):

                    st.session_state.records = imported

                    st.success("CSV 데이터를 불러왔습니다.")

                    st.rerun()

        except Exception:

            st.error(
                "CSV를 읽지 못했습니다. "
                "UTF-8 형식의 CSV 파일인지 확인해 주세요."
            )

    with st.expander("초기 예시 데이터로 되돌리기"):

        st.warning(
            "현재 세션에서 추가하거나 불러온 "
            "잔반 데이터가 초기화됩니다."
        )

        if st.button("예시 데이터 복원"):

            st.session_state.records = pd.DataFrame(
                INITIAL_DATA
            )

            st.success("예시 데이터로 복원했습니다.")

            st.rerun()


st.divider()

st.caption(
    "숨은 한입 | 급식 잔반 감축을 위한 교육용 프로토타입 "
    "| 실제 운영 시 데이터 저장소와 식품안전 지침을 별도로 검토하세요."
)
