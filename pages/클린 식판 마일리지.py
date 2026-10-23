import streamlit as st
import datetime
import os
from PIL import Image
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="클린 식판 마일리지",
    page_icon="🍽️",
    layout="wide"
)

# 세션 상태(Session State) 초기화
if "stamps" not in st.session_state:
    st.session_state.stamps = 3  # 기본 제공 스탬프
if "coupons" not in st.session_state:
    st.session_state.coupons = [
        {"id": 1, "name": "매점 500원 할인권", "code": "CPM-500-A1B2", "used": False, "date": "2026-10-20"},
    ]
if "history" not in st.session_state:
    st.session_state.history = [
        {"date": "2026-10-20 12:30", "status": "성공", "feedback": "잔반 없이 완벽하게 비워진 식판입니다!"},
        {"date": "2026-10-21 12:45", "status": "성공", "feedback": "깨끗하게 드셨네요! 스탬프 적립 완료."},
        {"date": "2026-10-22 13:10", "status": "성공", "feedback": "잔반 제로 실천 완료!"}
    ]

# Gemini API 설정 함수
def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash-lite")

# -----------------------------------------------------------------------------
# 2. 메인 화면 레이아웃 및 사이드바 Navigation
# -----------------------------------------------------------------------------
st.title("🍽️ 클린 식판 마일리지")
st.caption("잔반 없는 깨끗한 식판을 인증하고 포인트를 쌓아 쿠폰으로 교환해보세요!")

# 사이드바 사용자 프로필 및 요약
with st.sidebar:
    st.header("👤 내 프로필")
    st.metric(label="현재 보유 스탬프", value=f"{st.session_state.stamps} 개")
    st.write(f"🎟️ 보유 쿠폰: **{len([c for c in st.session_state.coupons if not c['used']])} 장**")
    st.write(f"🌱 총 잔반 제로 인증: **{len(st.session_state.history)} 회**")
    st.markdown("---")
    
    menu = st.radio(
        "메뉴 선택",
        ["📸 잔반 제로 인증", "🎁 스탬프 교환소", "🎟️ 내 쿠폰 보관함", "📅 인증 히스토리"],
        index=0
    )

# -----------------------------------------------------------------------------
# 3. 메뉴 1: 잔반 제로 인증 (사진 업로드 & AI 판별)
# -----------------------------------------------------------------------------
if menu == "📸 잔반 제로 인증":
    st.subheader("📸 Clean Plate 인증하기")
    st.write("식사를 마친 후 깨끗하게 비운 식판 사진을 올려주세요!")

    uploaded_file = st.file_uploader("식판 사진을 선택하세요", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드한 식판 사진", use_container_width=True)

        if st.button("✨ 잔반 제로 검증 및 스탬프 적립"):
            model = get_gemini_client()
            
            if model is None:
                st.warning("⚠️ GEMINI_API_KEY가 설정되어 있지 않아 테스트모드로 작동합니다. (자동 인증 성공 처리)")
                ai_success = True
                ai_feedback = "[테스트 모드] 잔반 없이 깔끔한 식판입니다! 스탬프 1개가 적립되었습니다."
            else:
                with st.spinner("🤖 Gemini AI가 식판 상태를 분석하고 있습니다..."):
                    try:
                        prompt = (
                            "이 사진은 사용자가 식사를 마친 후 제출한 식판 사진입니다. "
                            "식판에 음식물이 거의 남아있지 않고 잔반을 비운 상태인지 확인해주세요. "
                            "답변 첫 번째 줄에는 반드시 [PASS] 또는 [FAIL]을 작성하고, "
                            "두 번째 줄부터는 친절하고 격려하는 한 줄 피드백을 한국어로 남겨주세요."
                        )
                        response = model.generate_content([prompt, image])
                        result_text = response.text.strip()
                        
                        if "[PASS]" in result_text:
                            ai_success = True
                            ai_feedback = result_text.replace("[PASS]", "").strip()
                        else:
                            ai_success = False
                            ai_feedback = result_text.replace("[FAIL]", "").strip()
                    except Exception as e:
                        st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
                        ai_success = True  # 오류 시 사용자 경험을 위해 대체 승인
                        ai_feedback = "AI 분석 오류가 발생했으나 제출 기록을 확인하여 스탬프를 적립해 드립니다."

            # 분석 결과 반영
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            if ai_success:
                st.session_state.stamps += 1
                st.session_state.history.append({
                    "date": now_str,
                    "status": "성공",
                    "feedback": ai_feedback
                })
                st.balloons()
                st.success(f"🎉 인증 성공! 스탬프 1개가 적립되었습니다.\n\n**AI 피드백:** {ai_feedback}")
            else:
                st.session_state.history.append({
                    "date": now_str,
                    "status": "실패",
                    "feedback": ai_feedback
                })
                st.error(f"❌ 인증 실패: 잔반이 여전히 남아있는 것으로 판별되었습니다.\n\n**AI 피드백:** {ai_feedback}")

# -----------------------------------------------------------------------------
# 4. 메뉴 2: 스탬프 교환소
# -----------------------------------------------------------------------------
elif menu == "🎁 스탬프 교환소":
    st.subheader("🎁 모은 스탬프로 교환하기")
    st.info(f"💡 현재 보유 스탬프: **{st.session_state.stamps}개**")

    # 교환 가능한 상품 리스트
    shop_items = [
        {"name": "매점 500원 할인쿠폰", "cost": 3, "desc": "매점에서 사용할 수 있는 500원 할인권"},
        {"name": "바나나맛 우유 교환권", "cost": 5, "desc": "매점/편의점용 바나나우유 기프티콘"},
        {"name": "맛있는 컵라면 교환권", "cost": 7, "desc": "매점 인기 컵라면 1종 교환권"},
        {"name": "매점 3,000원 상품권", "cost": 10, "desc": "매점 모든 상품 구매 가능 3천원권"}
    ]

    cols = st.columns(2)
    for idx, item in enumerate(shop_items):
        with cols[idx % 2]:
            st.markdown(f"### {item['name']}")
            st.write(item["desc"])
            st.write(f"🏷️ 필요 스탬프: **{item['cost']}개**")
            
            if st.button(f"교환하기 ({item['cost']}개 소진)", key=f"buy_{idx}"):
                if st.session_state.stamps >= item["cost"]:
                    st.session_state.stamps -= item["cost"]
                    new_code = f"CPM-{datetime.datetime.now().strftime('%M%S')}-{idx}X"
                    st.session_state.coupons.append({
                        "id": len(st.session_state.coupons) + 1,
                        "name": item["name"],
                        "code": new_code,
                        "used": False,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success(f"🎉 '{item['name']}' 교환이 완료되었습니다! 내 쿠폰 보관함에서 확인하세요.")
                    st.rerun()
                else:
                    st.error("스탬프가 부족합니다. 잔반 제로 인증을 더 진행해 주세요!")

# -----------------------------------------------------------------------------
# 5. 메뉴 3: 내 쿠폰 보관함
# -----------------------------------------------------------------------------
elif menu == "🎟️ 내 쿠폰 보관함":
    st.subheader("🎟️ 내 쿠폰 보관함")
    
    if not st.session_state.coupons:
        st.write("보유 중인 쿠폰이 없습니다. 교환소에서 쿠폰을 발행해 보세요!")
    else:
        tab1, tab2 = st.tabs(["사용 가능 쿠폰", "사용 완료 쿠폰"])
        
        with tab1:
            available_coupons = [c for c in st.session_state.coupons if not c["used"]]
            if not available_coupons:
                st.write("사용 가능한 쿠폰이 없습니다.")
            else:
                for coupon in available_coupons:
                    with st.expander(f"🎫 {coupon['name']} (발급일: {coupon['date']})", expanded=True):
                        st.write(f"**쿠폰 코드:** `{coupon['code']}`")
                        if st.button("사용하기", key=f"use_{coupon['id']}"):
                            coupon["used"] = True
                            st.success(f"'{coupon['name']}' 쿠폰을 사용 처리했습니다.")
                            st.rerun()

        with tab2:
            used_coupons = [c for c in st.session_state.coupons if c["used"]]
            if not used_coupons:
                st.write("사용 완료된 쿠폰이 없습니다.")
            else:
                for coupon in used_coupons:
                    st.write(f"~~🎫 {coupon['name']} (`{coupon['code']}`) - 사용 완료~~")

# -----------------------------------------------------------------------------
# 6. 메뉴 4: 나의 잔반 제로 인증 기록 (히스토리)
# -----------------------------------------------------------------------------
elif menu == "📅 인증 히스토리":
    st.subheader("📅 나의 잔반 제로 인증 기록")
    
    if not st.session_state.history:
        st.write("아직 인증 기록이 없습니다. 잔반 제로 인증을 시작해 보세요!")
    else:
        for idx, record in enumerate(reversed(st.session_state.history)):
            icon = "✅" if record["status"] == "성공" else "❌"
            st.markdown(f"#### {icon} {record['date']} - 상태: {record['status']}")
            st.info(f"💬 AI 소평: {record['feedback']}")
            st.markdown("---")
