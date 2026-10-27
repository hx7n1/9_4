
elif page == "📝 실험 기록장":
    st.subheader("조리법을 바꾸고 결과를 기록해요")
    st.write("기록은 이 앱이 열려 있는 세션 동안 유지됩니다. 장기 보관하려면 CSV로 내려받으세요.")
    with st.form("experiment_form", clear_on_submit=True):
        exp_date = st.date_input("실험 날짜", value=date.today())
        exp_food = st.text_input("반찬 이름", placeholder="예: 당근볶음")
        exp_method = st.selectbox("시도한 조리법", ["잘게 다지기", "만두소로 활용", "전으로 만들기", "볶음밥에 섞기", "기타"])
        exp_before = st.number_input("변경 전 잔반량 (kg)", min_value=0.0, value=0.0, step=0.1)
        exp_after = st.number_input("변경 후 잔반량 (kg)", min_value=0.0, value=0.0, step=0.1)
        exp_note = st.text_area("관찰 메모", placeholder="식감 반응, 시식 의견, 제공량 변화 등")
        submitted = st.form_submit_button("실험 기록 저장", type="primary")
        if submitted:
            if not exp_food.strip():
                st.error("반찬 이름을 입력해 주세요.")
            elif exp_after > exp_before and exp_before == 0:
                st.warning("변경 전 잔반량이 0kg입니다. 입력값을 확인해 주세요.")
            else:
                improvement = ((exp_before - exp_after) / exp_before * 100) if exp_before > 0 else None
                st.session_state.experiments.append({
                    "날짜": exp_date.isoformat(),
                    "반찬": exp_food.strip(),
                    "조리법": exp_method,
                    "변경 전 잔반량(kg)": round(exp_before, 3),
                    "변경 후 잔반량(kg)": round(exp_after, 3),
                    "잔반 변화율(%)": round(improvement, 1) if improvement is not None else None,
                    "메모": exp_note.strip(),
                })
                st.success("실험 기록을 저장했습니다.")
    if st.session_state.experiments:
        exp_df = pd.DataFrame(st.session_state.experiments)
        st.dataframe(exp_df, use_container_width=True, hide_index=True)
        st.download_button(
            "실험 기록 CSV 다운로드",
            data=exp_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="hidden_bite_experiments.csv",
            mime="text/csv",
        )
        if st.button("실험 기록 모두 지우기"):
            st.session_state.experiments = []
            st.rerun()
    else:
        st.info("아직 실험 기록이 없습니다. 첫 조리 실험을 기록해 보세요.")

elif page == "📁 데이터 관리":
    st.subheader("잔반 기록 추가 또는 CSV 관리")
    with st.form("record_form", clear_on_submit=True):
        r_date = st.date_input("측정 날짜", value=date.today())
        r_food = st.text_input("반찬 이름", placeholder="예: 당근볶음")
        r_served = st.number_input("제공량 (kg)", min_value=0.0, value=1.0, step=0.1)
        r_waste = st.number_input("잔반량 (kg)", min_value=0.0, value=0.2, step=0.1)
        r_method = st.selectbox("조리법", ["기본 제공", "잘게 다지기", "만두소로 활용", "전으로 만들기", "볶음밥에 섞기", "기타"])
        r_note = st.text_input("메모 (선택)")
        add_record = st.form_submit_button("기록 추가", type="primary")
        if add_record:
            if not r_food.strip():
                st.error("반찬 이름을 입력해 주세요.")
            elif r_waste > r_served:
                st.error("잔반량은 제공량보다 클 수 없습니다.")
            else:
                new_row = {
                    "날짜": r_date.isoformat(),
                    "반찬": r_food.strip(),
                    "제공량(kg)": float(r_served),
                    "잔반량(kg)": float(r_waste),
                    "조리법": r_method,
                    "메모": r_note.strip(),
                }
                st.session_state.records = pd.concat(
                    [st.session_state.records, pd.DataFrame([new_row])], ignore_index=True
                )
                st.success("잔반 기록을 추가했습니다.")
                st.rerun()

    st.markdown("#### 현재 잔반 데이터")
    current_df = prepare_records(st.session_state.records)
    st.dataframe(current_df, use_container_width=True, hide_index=True)
    st.download_button(
        "현재 데이터 CSV 다운로드",
        data=current_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="hidden_bite_records.csv",
        mime="text/csv",
    )
    uploaded = st.file_uploader("CSV 파일로 데이터 불러오기", type=["csv"])
    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded)
            required = {"날짜", "반찬", "제공량(kg)", "잔반량(kg)"}
            if not required.issubset(set(imported.columns)):
                st.error("CSV에 날짜, 반찬, 제공량(kg), 잔반량(kg) 열이 필요합니다.")
            else:
                imported = prepare_records(imported)
                if (imported["잔반량(kg)"] > imported["제공량(kg)"]).any():
                    st.error("잔반량은 제공량보다 클 수 없습니다.")
                else:
                    st.dataframe(imported.head(10), use_container_width=True, hide_index=True)
                    if st.button("불러온 CSV로 현재 데이터 교체"):
                        st.session_state.records = imported
                        st.success("CSV 데이터를 불러왔습니다.")
                        st.rerun()
        except Exception as exc:
            st.error(f"CSV를 읽지 못했습니다. UTF-8 CSV 파일인지 확인해 주세요. ({exc})")

    with st.expander("초기 예시 데이터로 되돌리기"):
        st.warning("현재 세션에서 추가하거나 불러온 잔반 데이터가 초기화됩니다.")
        if st.button("예시 데이터 복원"):
            st.session_state.records = pd.DataFrame(INITIAL_DATA)
            st.success("예시 데이터로 복원했습니다.")
            st.rerun()

st.divider()
st.caption("숨은 한입 · 급식 잔반 감축을 위한 교육용 프로토타입 | 실제 운영 시 데이터 저장소와 학교 식품안전 지침을 별도로 검토하세요.")
