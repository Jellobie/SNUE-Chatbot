import streamlit as st
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 확인
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_api_key_here":
    st.error("⚠️ .env 파일에 GOOGLE_API_KEY를 설정해주세요!")
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
        st.write("---")
        st.success("### 🤖 AI 매니저의 분석 결과")
        
        # AI 분석 중 표시
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # Gemini API에 전달할 프롬프트 작성
                prompt = f"""6학년 학생을 위한 합리적 소비 학습 활동입니다.

상황 정보:
- 목적: {goal}
- 총 예산: {budget:,}원

대안 A:
- 가격: {price_a:,}원
- 만족도: {satisfaction_a}/10

대안 B:
- 가격: {price_b:,}원
- 만족도: {satisfaction_b}/10

다음 내용을 초등학교 6학년 학생이 이해하기 쉽게 분석해주세요:
1. 예산 범위 내에서 어떤 대안이 합리적인지
2. 기회비용 개념을 설명
3. 가격 대비 만족도를 고려한 추천
4. 최종 선택에 대한 조언

친근하고 격려하는 톤으로 작성해주세요."""

                # Gemini API 요청
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                response = requests.post(api_url, json=payload, headers=headers)
                response.raise_for_status()
                
                # 응답 파싱
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(ai_response)
                else:
                    # API 응답이 없을 경우 기본 분석 제공
                    score_a = satisfaction_a / price_a * 10000 if price_a > 0 else 0
                    score_b = satisfaction_b / price_b * 10000 if price_b > 0 else 0
                    
                    if score_a > score_b:
                        best = "대안 A"
                        st.write(f"추천 선택: **{best}**")
                        st.write(f"**이유:** 가격 대비 만족도가 더 높습니다.")
                    else:
                        best = "대안 B"
                        st.write(f"추천 선택: **{best}**")
                        st.write(f"**이유:** 더 경제적이거나 만족도가 높습니다.")
                    
                    st.warning(f"💡 **기회비용 확인:** {best}를 선택할 경우, 다른 대안을 포기하게 됩니다. 나의 선택이 최선인지 다시 한번 생각해보세요!")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API 요청 중 오류가 발생했습니다: {str(e)}")
                # 오류 발생 시 기본 분석 제공
                score_a = satisfaction_a / price_a * 10000 if price_a > 0 else 0
                score_b = satisfaction_b / price_b * 10000 if price_b > 0 else 0
                
                if score_a > score_b:
                    best = "대안 A"
                else:
                    best = "대안 B"
                
                st.write(f"추천 선택: **{best}**")
                st.warning(f"💡 **기회비용 확인:** {best}를 선택할 경우, 다른 대안을 포기하게 됩니다.")
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {str(e)}")

# [cite_start]5. 윤리적 고려 및 성찰 (AI 리터러시 목표 연계) [cite: 147, 148]
st.write("---")
st.caption("※ 주의: AI의 추천은 참고 자료일 뿐입니다. 최종 결정은 여러분의 가치관에 따라 직접 내리세요.")