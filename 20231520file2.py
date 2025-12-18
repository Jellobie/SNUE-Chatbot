import streamlit as st
import os
from dotenv import load_dotenv

# 현재 폴더에 있는 .env 파일을 읽어옵니다.
load_dotenv()

# 환경 변수에서 키를 가져옵니다.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 만약 키를 못 가져왔다면 에러 메시지 출력
if not GOOGLE_API_KEY:
    st.error("⚠️ .env 파일에서 GOOGLE_API_KEY를 찾을 수 없습니다! 파일명과 내용을 확인해주세요.")
    st.stop()

# 1. 학생들에게 보여질 메인 화면 제목 및 학습 목표 설정
st.title("🛒 우리 집 '합리적 소비' 매니저")
st.subheader("6학년 2학기 사회: 합리적 선택과 기회비용")

# [cite_start]2. 사이드바를 통한 상황 설정 (CK와 연계: 가계의 경제 활동) [cite: 107]
with st.sidebar:
    st.header("📋 소비 상황 설정")
    budget = st.number_input("오늘의 총 예산 (원):", min_value=0, value=50000, step=1000)
    goal = st.text_input("구매하려는 목적 (예: 저녁 식사 재료):")

# [cite_start]3. 데이터 입력창 생성: 학생들이 대안을 비교할 수 있도록 함 [cite: 108]
st.info(f"목표: **{goal}**을(를) 위해 **{budget:,}원** 안에서 가장 합리적인 선택을 해보세요!")

col1, col2 = st.columns(2)

with col1:
    st.write("### 대안 A")
    price_a = st.number_input("A 상품 가격 (원):", min_value=0, value=0, key="a_p")
    satisfaction_a = st.slider("A 상품 만족도 (1-10):", 1, 10, 5, key="a_s")

with col2:
    st.write("### 대안 B")
    price_b = st.number_input("B 상품 가격 (원):", min_value=0, value=0, key="b_p")
    satisfaction_b = st.slider("B 상품 만족도 (1-10):", 1, 10, 5, key="b_s")

# [cite_start]4. 분석 버튼: AI가 기회비용과 합리성을 판단하여 피드백 제공 [cite: 109, 122]
if st.button("AI 매니저에게 분석 요청하기"):
    if price_a > budget and price_b > budget:
        st.error("두 대안 모두 예산을 초과합니다. 합리적 선택의 첫걸음은 예산 범위 준수입니다!")
    else:
        # 간단한 합리성 지수 계산 (만족도 / 가격 * 10000)
        score_a = satisfaction_a / price_a * 10000 if price_a > 0 else 0
        score_b = satisfaction_b / price_b * 10000 if price_b > 0 else 0
        
        st.write("---")
        st.success("### 🤖 AI 매니저의 분석 결과")
        
        # [cite_start]기회비용 개념 가시화 (TCK) [cite: 195]
        if score_a > score_b:
            best = "대안 A"
            opp_cost = price_a  # 선택으로 인해 포기한 가치(단순화)
            st.write(f"추천 선택: **{best}**")
            st.write(f"**이유:** 가격 대비 만족도가 더 높습니다.")
        else:
            best = "대안 B"
            st.write(f"추천 선택: **{best}**")
            st.write(f"**이유:** 더 경제적이거나 만족도가 높습니다.")

        st.warning(f"💡 **기회비용 확인:** {best}를 선택할 경우, 다른 대안을 포기하게 됩니다. 나의 선택이 최선인지 다시 한번 생각해보세요!")

# [cite_start]5. 윤리적 고려 및 성찰 (AI 리터러시 목표 연계) [cite: 147, 148]
st.write("---")
st.caption("※ 주의: AI의 추천은 참고 자료일 뿐입니다. 최종 결정은 여러분의 가치관에 따라 직접 내리세요.")