import streamlit as st
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드 (로컬 환경용)
load_dotenv()

# API 키 확인 - Streamlit Cloud의 경우 secrets 사용, 로컬의 경우 .env 사용
GOOGLE_API_KEY = None
try:
    # Streamlit Cloud에서는 secrets 사용
    if hasattr(st, 'secrets') and "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# secrets에 없으면 .env에서 가져오기 (로컬 환경용)
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 만약 키를 못 가져왔다면 에러 메시지 출력
if not GOOGLE_API_KEY:
    st.error("⚠️ Streamlit Secrets 또는 .env 파일에서 GOOGLE_API_KEY를 찾을 수 없습니다!")
    st.error("로컬 실행: .env 파일을 확인하세요.")
    st.error("Streamlit Cloud: Secrets에 GOOGLE_API_KEY를 설정하세요.")
    st.stop()

# 1. 메인 화면 설정 및 사용자 시선 집중
st.title("🛒 우리 집 '합리적 소비' 매니저")
st.subheader("합리적으로 선택해 보아요.") # 요구사항 1 반영

# 2. 주제 및 기준 데이터 사전 정의 (내용 지식 CK와 연계)
# [cite_start]주제별로 하위 항목과 평가 기준을 다르게 설정하여 탐구의 깊이를 더함 [cite: 106]
THEMES = {
    "음식": {
        "items": ["치킨", "피자", "햄버거", "떡볶이"],
        "criteria": ["맛", "양(포만감)", "배달 속도", "영양 성분"]
    },
    "신발": {
        "items": ["운동화", "구두", "샌들", "슬리퍼"],
        "criteria": ["디자인", "착용감(편안함)", "내구성", "브랜드 가치"]
    },
    "가방": {
        "items": ["백팩", "에코백", "크로스백", "캐리어"],
        "criteria": ["디자인", "수납 공간", "무게", "재질"]
    },
    "학용품": {
        "items": ["연필", "샤프", "볼펜", "만년필"],
        "criteria": ["디자인", "필기감", "내구성", "가격 대비 성능"]
    }
}

# [cite_start]3. 주목도 높은 예산 및 주제 설정 영역 (TK 기능 활용) [cite: 108, 110]
st.divider()
st.write("### 💰 탐구 시작하기")
col_start1, col_start2 = st.columns(2)

with col_start1:
    # 학생들이 가장 먼저 결정해야 할 '주제' 선택창
    choice_theme = st.selectbox("어떤 물건을 사고 싶나요?", list(THEMES.keys()))

with col_start2:
    # 주목을 끌 수 있는 큰 입력창으로 예산 설정 (요구사항 2 반영)
    budget = st.number_input("💵 오늘 쓸 수 있는 최대 예산은? (원)", min_value=0, value=30000, step=1000)

# 4. 대안 선택 및 다각적 점수 매기기 (요구사항 3, 4 반영)
# [cite_start]단순히 가격만 보는 것이 아니라 여러 가치를 비교하게 함 [cite: 111]
st.info(f"선택한 주제: **{choice_theme}** | 목표: **{budget:,}원** 안에서 가장 가치 있는 선택을 하세요!")

col_a, col_b = st.columns(2)
items_list = THEMES[choice_theme]["items"]
criteria_list = THEMES[choice_theme]["criteria"]

# 대안 A 설정 영역
with col_a:
    st.markdown("#### 🅰️ 대안 A")
    item_a = st.selectbox("첫 번째 후보", items_list, key="item_a")
    price_a = st.number_input(f"{item_a}의 가격 (원)", min_value=0, value=0, key="p_a")
    
    st.write("✨ **평가 점수 (각 10점 만점)**")
    scores_a = []
    for crit in criteria_list:
        score = st.slider(f"{item_a} - {crit}", 0, 10, 5, key=f"a_{crit}")
        scores_a.append(score)
    avg_a = sum(scores_a) / len(scores_a)

# 대안 B 설정 영역
with col_b:
    st.markdown("#### 🅱️ 대안 B")
    item_b = st.selectbox("두 번째 후보", items_list, key="item_b")
    price_b = st.number_input(f"{item_b}의 가격 (원)", min_value=0, value=0, key="p_b")
    
    st.write("✨ **평가 점수 (각 10점 만점)**")
    scores_b = []
    for crit in criteria_list:
        score = st.slider(f"{item_b} - {crit}", 0, 10, 5, key=f"b_{crit}")
        scores_b.append(score)
    avg_b = sum(scores_b) / len(scores_b)

# [cite_start]5. AI 매니저의 복합적 분석 및 피드백 (AI-TPACK의 핵심: TPK) [cite: 117, 121]
if st.button("🤖 AI 매니저에게 합리성 분석 요청하기"):
    st.divider()
    
    # 예산 초과 여부 먼저 확인
    if price_a > budget and price_b > budget:
        st.error(f"🚨 경고: 두 상품 모두 예산({budget:,}원)을 초과합니다. 다른 상품을 찾아보세요!")
    elif price_a == 0 or price_b == 0:
        st.warning("분석을 위해 상품의 가격을 입력해주세요.")
    else:
        st.success("### 📊 AI 매니저의 가치 분석 리포트")
        
        # AI 분석 중 표시
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # Gemini API에 전달할 프롬프트 작성
                prompt = f"""초등학교 6학년 학생을 위한 합리적 소비 학습 활동입니다.

상황 정보:
- 주제: {choice_theme}
- 목표 예산: {budget:,}원

대안 A: {item_a}
- 가격: {price_a:,}원
- 평가 점수:
"""
                for i, crit in enumerate(criteria_list):
                    prompt += f"  - {crit}: {scores_a[i]}/10점\n"
                prompt += f"- 평균 만족도: {avg_a:.1f}/10점\n\n"

                prompt += f"""대안 B: {item_b}
- 가격: {price_b:,}원
- 평가 점수:
"""
                for i, crit in enumerate(criteria_list):
                    prompt += f"  - {crit}: {scores_b[i]}/10점\n"
                prompt += f"- 평균 만족도: {avg_b:.1f}/10점\n\n"

                prompt += """다음 내용을 초등학교 6학년 학생이 이해하기 쉽게 분석해주세요:
1. 예산 범위 내에서 어떤 대안이 합리적인지
2. 각 평가 기준(맛, 디자인 등)을 고려한 종합적 분석
3. 기회비용 개념을 설명
4. 가격 대비 만족도를 고려한 추천
5. 최종 선택에 대한 조언

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
                    value_a = avg_a / price_a * 10000 if price_a <= budget else -1
                    value_b = avg_b / price_b * 10000 if price_b <= budget else -1
                    
                    if value_a > value_b:
                        best_item, best_avg, opp_item = item_a, avg_a, item_b
                    else:
                        best_item, best_avg, opp_item = item_b, avg_b, item_a
                    
                    st.write(f"✅ 추천: **{best_item}**을(를) 선택하는 것이 더 합리적입니다.")
                    st.write(f"- 선택한 상품의 평균 만족도: **{best_avg:.1f}점**")
                    st.write(f"- 💡 **기회비용 확인:** {best_item}을 선택함으로써 포기하게 되는 {opp_item}의 가치도 고려했나요?")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API 요청 중 오류가 발생했습니다: {str(e)}")
                # 오류 발생 시 기본 분석 제공
                value_a = avg_a / price_a * 10000 if price_a <= budget else -1
                value_b = avg_b / price_b * 10000 if price_b <= budget else -1
                
                if value_a > value_b:
                    best_item, best_avg, opp_item = item_a, avg_a, item_b
                else:
                    best_item, best_avg, opp_item = item_b, avg_b, item_a
                
                st.write(f"✅ 추천: **{best_item}**을(를) 선택하는 것이 더 합리적입니다.")
                st.write(f"- 선택한 상품의 평균 만족도: **{best_avg:.1f}점**")
                st.write(f"- 💡 **기회비용 확인:** {best_item}을 선택함으로써 포기하게 되는 {opp_item}의 가치도 고려했나요?")
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        
        # [cite_start]비판적 사고 유도 [cite: 87, 88]
        st.info("⚠️ AI는 수치로만 계산합니다. 여러분의 특별한 취향이나 상황에 따라 결과는 달라질 수 있습니다.")

# [cite_start]6. 윤리적 고려 및 성찰 (AI 리터러시 목표 연계) [cite: 147, 148]
st.divider()
st.caption("※ 주의: AI의 추천은 참고 자료일 뿐입니다. 최종 결정은 여러분의 가치관에 따라 직접 내리세요.")
