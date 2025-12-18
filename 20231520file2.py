import streamlit as st
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


# 1. 메인 화면 및 학습 목표 설정
st.title("🛒 우리 집 '합리적 소비' 매니저")
st.subheader("합리적으로 선택해 보아요.")

# 2. 주제별 데이터 정의 (내용 지식 CK 연계)
THEMES = {
    "음식": {
        "items": ["치킨", "피자", "햄버거", "떡볶이"],
        "criteria": ["맛", "양(포만감)", "배달 속도"]
    },
    "신발": {
        "items": ["운동화", "구두", "샌들", "슬리퍼"],
        "criteria": ["디자인", "착용감", "내구성"]
    },
    "가방": {
        "items": ["백팩", "에코백", "크로스백", "캐리어"],
        "criteria": ["디자인", "수납 공간", "무게"]
    },
    "학용품": {
        "items": ["연필", "샤프", "볼펜", "만년필"],
        "criteria": ["디자인", "필기감", "내구성"]
    }
}

# 3. 예산 및 주제 설정
st.divider()
st.write("### 💰 탐구 시작하기")
col_start1, col_start2 = st.columns(2)

with col_start1:
    choice_theme = st.selectbox("어떤 물건을 사고 싶나요?", list(THEMES.keys()))

with col_start2:
    budget = st.number_input("💵 오늘 쓸 수 있는 최대 예산은? (원)", min_value=0, value=30000, step=1000)

st.info(f"현재 주제: **{choice_theme}** | 나의 예산: **{budget:,}원**")

# 4. 대안 입력 및 다각적 평가 (가격을 점수에 포함)
col_a, col_b = st.columns(2)
items_list = THEMES[choice_theme]["items"]
criteria_list = THEMES[choice_theme]["criteria"]

# 가격을 점수(0~10점)로 환산하는 로직: 예산에 가까울수록 0점, 0원에 가까울수록 10점
def calculate_price_score(price, budget):
    if price > budget: return 0
    if budget == 0: return 0
    return (1 - (price / budget)) * 10 

# --- 대안 A 설정 ---
with col_a:
    st.markdown("#### 🅰️ 대안 A")
    item_a = st.selectbox("첫 번째 후보", items_list, key="item_a")
    price_a = st.number_input(f"{item_a} 가격 (원)", min_value=0, value=0, key="p_a")
    
    st.write("**✨ 항목별 만족도 점수**")
    scores_a = []
    for crit in criteria_list:
        s = st.slider(f"{item_a} - {crit}", 0, 10, 5, key=f"a_{crit}")
        scores_a.append(s)
    
    # 경제성 점수 자동 계산 및 합산
    p_score_a = calculate_price_score(price_a, budget)
    st.caption(f"💰 경제성 점수(자동): {p_score_a:.1f}/10점")
    scores_a.append(p_score_a)
    avg_a = sum(scores_a) / len(scores_a)

# --- 대안 B 설정 ---
with col_b:
    st.markdown("#### 🅱️ 대안 B")
    item_b = st.selectbox("두 번째 후보", items_list, key="item_b")
    price_b = st.number_input(f"{item_b} 가격 (원)", min_value=0, value=0, key="p_b")
    
    st.write("**✨ 항목별 만족도 점수**")
    scores_b = []
    for crit in criteria_list:
        s = st.slider(f"{item_b} - {crit}", 0, 10, 5, key=f"b_{crit}")
        scores_b.append(s)
        
    p_score_b = calculate_price_score(price_b, budget)
    st.caption(f"💰 경제성 점수(자동): {p_score_b:.1f}/10점")
    scores_b.append(p_score_b)
    avg_b = sum(scores_b) / len(scores_b)

# 5. AI 매니저 분석 결과 출력
if st.button("🤖 AI 매니저에게 합리성 분석 요청하기"):
    st.divider()
    if price_a > budget and price_b > budget:
        st.error(f"🚨 두 상품 모두 예산({budget:,}원)을 초과했습니다!")
    elif price_a == 0 or price_b == 0:
        st.warning("분석을 위해 상품 가격을 입력해주세요.")
    else:
        st.success("### 📊 AI 매니저의 종합 가치 분석")
        
        if avg_a > avg_b:
            best, diff, opp = item_a, avg_a - avg_b, item_b
        else:
            best, diff, opp = item_b, avg_b - avg_a, item_a
            
        st.write(f"✅ AI 추천: **{best}**가 대안보다 약 **{diff:.1f}점** 더 합리적입니다.")
        st.warning(f"💡 **기회비용 확인:** {best}를 선택함으로써 {opp}의 장점들을 포기하게 됨을 잊지 마세요!")
        st.info("⚠️ 최종 결정은 AI가 아닌 여러분의 가치관에 따라 내려야 합니다.")