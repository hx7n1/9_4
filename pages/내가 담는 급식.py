import streamlit as st
import csv
import io
from datetime import date, datetime

st.set_page_config(
    page_title="내가 담는 급식",
    page_icon="🍱",
    layout="wide",
)

# ---------- 기본 설정 ----------
st.markdown(
    """
    <style>
    .stApp { background-color: #fffdf7; }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #285943;
        margin-bottom: 0;
    }
    .sub-title {
        color: #6c776f;
        font-size: 1rem;
        margin-top: 5px;
    }
    div[data-testid="stMetric"] {
        background: #f0f7ed;
        border: 1px solid #dcebd5;
        padding: 16px;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "meal_records" not in st.session_state:
    st.session_state.meal_records = []

st.markdown(
    '<p class="main-title">🍱 내가 담는 급식</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">'
    '먹을 만큼 담고, 남기는 음식은 줄여 봐요!'
    '</p>',
    unsafe_allow_html=True,
)

st.divider()

# 잔반 선택지별 기록용 수치
LEFTOVER_VALUES = {
    "남김 없음": 0.0,
    "조금 남김 (약 1/4)": 0.25,
    "절반 정도 남김": 0.5,
    "대부분 남김 (약 3/4)": 0.75,
    "거의 다 남김": 1.0,
}

PORTION_VALUES = {
    "적게 담기": 0.75,
    "보통 담기": 1.0,
    "많이 담기": 1.25,
}

tab_record, tab_dashboard, tab_history = st.tabs(
    ["🥄 급식 기록하기", "📊 잔반 대시보드", "📋 기록 확인하기"]
)

# ---------- 급식 기록 ----------
with tab_record:
    st.subheader("오늘은 먹을 만큼만 담아 봐요!")
    st.write(
        "급식 메뉴와 내가 받은 양, 식사 후 남긴 양을 기록해 주세요."
    )

    with st.form("meal_form", clear_on_submit=True):
        meal_date = st.date_input("식사 날짜", value=date.today())

        menu = st.text_input(
            "오늘의 급식 메뉴",
            placeholder="예: 카레라이스, 미역국, 김치",
            max_chars=200,
        )

        st.markdown("#### 내가 담은 양")
        portion = st.radio(
            "평소와 비교해서 얼마나 담았나요?",
            list(PORTION_VALUES.keys()),
            horizontal=True,
        )

        st.markdown("#### 식사 후 남긴 양")
        leftover = st.select_slider(
            "받은 음식 중 얼마나 남겼나요?",
            options=list(LEFTOVER_VALUES.keys()),
            value="남김 없음",
        )

        reason = st.selectbox(
            "음식을 남긴 이유",
            [
                "남기지 않았어요",
                "양이 너무 많았어요",
                "입맛에 맞지 않았어요",
                "배가 불렀어요",
                "시간이 부족했어요",
                "기타",
            ],
        )

        memo = st.text_input(
            "한마디 메모 (선택)",
            placeholder="예: 다음에는 밥을 조금만 받을래요.",
            max_chars=200,
        )

        submitted = st.form_submit_button(
            "✅ 오늘의 급식 기록 저장",
            use_container_width=True,
        )

    if submitted:
        if not menu.strip():
            st.error("급식 메뉴를 한 가지 이상 입력해 주세요.")
        else:
            record = {
                "date": meal_date.isoformat(),
                "menu": menu.strip(),
                "portion": portion,
                "portion_value": PORTION_VALUES[portion],
                "leftover": leftover,
                "leftover_value": LEFTOVER_VALUES[leftover],
                "reason": reason,
                "memo": memo.strip(),
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.meal_records.append(record)
            st.success("기록을 저장했어요! 내일도 먹을 만큼만 담아 봐요. 🌱")

            if leftover == "남김 없음":
                st.balloons()
                st.info("멋져요! 오늘은 잔반 없이 식사를 마쳤어요.")
            elif reason == "양이 너무 많았어요":
                st.info("다음에는 적게 담고, 부족하면 더 받는 방법을 시도해 보세요.")

# ---------- 대시보드 ----------
with tab_dashboard:
    st.subheader("나의 잔반 줄이기 현황")
    records = st.session_state.meal_records

    if not records:
        st.info("아직 기록이 없어요. '급식 기록하기'에서 첫 기록을 남겨 보세요!")
    else:
        total = len(records)
        no_leftover = sum(
            1 for r in records if r["leftover_value"] == 0
        )
        avg_leftover = (
            sum(r["leftover_value"] for r in records) / total * 100
        )
        success_rate = no_leftover / total * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("기록한 식사", f"{total}회")
        c2.metric("잔반 없는 식사", f"{no_leftover}회")
        c3.metric("잔반 없는 비율", f"{success_rate:.0f}%")

        st.markdown("#### 📉 기록상 잔반 정도")
        st.progress(min(1.0, max(0.0, 1.0 - avg_leftover / 100)))
        st.caption(
            f"선택한 잔반 수준의 평균은 {avg_leftover:.0f}%예요. "
            "실제 음식 무게가 아닌 선택지 기반의 참고 수치입니다."
        )

        st.markdown("#### 🌱 나의 작은 목표")
        if success_rate >= 80:
            st.success("좋아요! 지금의 습관을 꾸준히 이어 가요.")
        elif avg_leftover >= 50:
            st.warning(
                "다음 급식에서는 처음에 조금만 담고, "
                "더 먹고 싶을 때 추가로 받아 보세요."
            )
        else:
            st.info(
                "남기는 이유를 살펴보고, 내게 맞는 양을 찾아봐요."
            )

        st.markdown("#### 🍽️ 음식을 남긴 이유")
        reason_counts = {}
        for r in records:
            if r["reason"] != "남기지 않았어요":
                reason_counts[r["reason"]] = (
                    reason_counts.get(r["reason"], 0) + 1
                )

        if reason_counts:
            st.bar_chart(reason_counts)
        else:
            st.write("아직 기록된 잔반 이유가 없어요. 아주 좋아요!")

        st.markdown("#### 📅 날짜별 잔반 수준")
        daily = {}
        for r in records:
            d = r["date"]
            daily.setdefault(d, []).append(r["leftover_value"] * 100)

        daily_avg = {
            d: round(sum(values) / len(values), 1)
            for d, values in sorted(daily.items())
        }
        st.line_chart(daily_avg)

# ---------- 기록 확인 및 CSV 다운로드 ----------
with tab_history:
    st.subheader("내가 기록한 급식")

    records = st.session_state.meal_records

    if not records:
        st.info("저장된 기록이 없습니다.")
    else:
        for i, r in enumerate(reversed(records)):
            with st.expander(
                f"{r['date']} · {r['menu']} · {r['leftover']}"
            ):
                st.write(f"**담은 양:** {r['portion']}")
                st.write(f"**남긴 이유:** {r['reason']}")
                if r["memo"]:
                    st.write(f"**메모:** {r['memo']}")
                st.caption(f"저장 시각: {r['saved_at']}")

        st.markdown("#### 📥 기록 내려받기")
        csv_buffer = io.StringIO()
        fieldnames = [
            "date", "menu", "portion", "leftover",
            "reason", "memo", "saved_at",
        ]
        writer = csv.DictWriter(
            csv_buffer,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(records)

        # Excel에서 한글이 깨지지 않도록 BOM 추가
        csv_bytes = ("\ufeff" + csv_buffer.getvalue()).encode("utf-8")

        st.download_button(
            label="CSV 파일 다운로드",
            data=csv_bytes,
            file_name=f"급식_잔반기록_{date.today().isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.caption(
            "주의: 현재 기록은 앱 세션에 저장됩니다. "
            "앱이 재시작되거나 세션이 초기화되면 사라질 수 있으니 "
            "CSV 파일로 보관해 주세요."
        )

        if st.button("🗑️ 전체 기록 초기화", type="secondary"):
            st.session_state.meal_records = []
            st.rerun()

st.divider()
st.caption(
    "🌿 내가 먹을 만큼 담는 작은 실천이 음식물 쓰레기를 줄이는 시작입니다."
)

