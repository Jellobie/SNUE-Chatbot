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


# 1. 한국어 조사(이/가, 을/를) 자동 처리 함수
# 목적: 상품명 받침 유무를 판별하여 "치킨이", "초밥을" 등 자연스러운 문장을 구성함
def get_josa(word, josa_type):
    if not word: return ""
    last_char = word[-1]
    if '가' <= last_char <= '힣':
        char_code = ord(last_char) - 44032
        has_batchim = (char_code % 28 != 0)
        if josa_type == "이/가":
            return f"{word}이" if has_batchim else f"{word}가"
        elif josa_type == "을/를":
            return f"{word}을" if has_batchim else f"{word}를"
    return word

# 2. 메인 화면 및 학습 목표 설정
# 결과: 학생이 수업의 주제와 목적을 명확히 인지하도록 제목 출력
st.title("🛒 우리 집 '합리적 소비' 매니저")
st.subheader("합리적으로 선택해 보아요.")

# 3. 주제별 데이터 정의 (교과 내용 CK 연계)
THEMES = {
    "음식": {"items": ["치킨", "피자", "햄버거", "떡볶이"], "criteria": ["맛", "양", "배달 속도"]},
    "신발": {"items": ["운동화", "구두", "샌들", "슬리퍼"], "criteria": ["디자인", "착용감", "내구성"]},
    "가방": {"items": ["백팩", "에코백", "크로스백", "캐리어"], "criteria": ["디자인", "수납 공간", "무게"]},
    "학용품": {"items": ["연필", "샤프", "볼펜", "만년필"], "criteria": ["디자인", "필기감", "내구성"]}
}

# 4. 예산 및 주제 설정 영역
st.divider()
st.write("### 💰 탐구 시작하기")
col_start1, col_start2 = st.columns(2)

with col_start1:
    choice_theme = st.selectbox("어떤 물건을 사고 싶나요?", list(THEMES.keys()))

with col_start2:
    # 목적: 자원의 희소성을 체감하도록 예산 제약 조건 설정
    budget = st.number_input("💵 오늘 쓸 수 있는 최대 예산은? (원)", min_value=0, value=30000, step=1000)

st.info(f"현재 주제: **{choice_theme}** | 나의 예산: **{budget:,}원**")

# 5. 경제성 점수 환산 함수
def calculate_price_score(price, budget):
    if price > budget or budget == 0: return 0
    return (1 - (price / budget)) * 10 

# 6. 대안 입력 및 다각적 평가 영역 (CK-TK 통합)
col_a, col_b = st.columns(2)
items_list = THEMES[choice_theme]["items"]
criteria_list = THEMES[choice_theme]["criteria"]

# --- 대안 A 설정 ---
with col_a:
    st.markdown("#### 🅰️ 대안 A")
    item_a_sel = st.selectbox("후보 선택", items_list + ["직접 입력"], key="item_a_sel")
    item_a = st.text_input("상품 이름", key="item_a_custom") if item_a_sel == "직접 입력" else item_a_sel
    price_a = st.number_input(f"{item_a} 가격 (원)", min_value=0, value=0, key="p_a")
    
    # 결과: 학생이 여러 가치 기준에 따라 직접 슬라이더를 조절하여 데이터를 생성함
    scores_a_val = [st.slider(f"{item_a} - {crit}", 0, 10, 5, key=f"a_{crit}") for crit in criteria_list]
    p_score_a = calculate_price_score(price_a, budget)
    st.caption(f"💰 경제성 점수: {p_score_a:.1f}/10점")
    
    # 평가 항목 리스트와 점수를 딕셔너리로 저장하여 분석에 활용
    eval_a = dict(zip(criteria_list + ["경제성"], scores_a_val + [p_score_a]))
    avg_a = sum(eval_a.values()) / len(eval_a)

# --- 대안 B 설정 ---
with col_b:
    st.markdown("#### 🅱️ 대안 B")
    item_b_sel = st.selectbox("후보 선택", items_list + ["직접 입력"], key="item_b_sel")
    item_b = st.text_input("상품 이름", key="item_b_custom") if item_b_sel == "직접 입력" else item_b_sel
    price_b = st.number_input(f"{item_b} 가격 (원)", min_value=0, value=0, key="p_b")
    
    scores_b_val = [st.slider(f"{item_b} - {crit}", 0, 10, 5, key=f"b_{crit}") for crit in criteria_list]
    p_score_b = calculate_price_score(price_b, budget)
    st.caption(f"💰 경제성 점수: {p_score_b:.1f}/10점")
    
    eval_b = dict(zip(criteria_list + ["경제성"], scores_b_val + [p_score_b]))
    avg_b = sum(eval_b.values()) / len(eval_b)

# 7. AI 매니저 분석 및 기회비용 상세 피드백
if st.button("🤖 AI 매니저에게 합리성 분석 요청하기"):
    st.divider()
    if price_a > budget and price_b > budget:
        st.error(f"🚨 예산({budget:,}원) 내에서 선택 가능한 상품이 없습니다.")
    elif price_a == 0 or price_b == 0:
        st.warning("분석을 위해 가격을 입력해주세요.")
    else:
        st.success("### 📊 AI 매니저의 종합 가치 분석")
        
        # 합리적 선택지 선정
        if avg_a > avg_b:
            best, other, b_eval, o_eval, b_avg, o_avg = item_a, item_b, eval_a, eval_b, avg_a, avg_b
        else:
            best, other, b_eval, o_eval, b_avg, o_avg = item_b, item_a, eval_b, eval_a, avg_b, avg_a
            
        diff = b_avg - o_avg
        st.write(f"✅ AI 추천: **{get_josa(best, '이/가')} {other}보다** 약 **{diff:.1f}점** 더 합리적입니다.")
        
        # 기회비용 상세 분석 로직: 선택하지 않은 쪽이 더 우수했던 항목 추출 (TK)
        # 목적: 포기하게 되는 구체적인 가치를 데이터 기반으로 제시하여 비판적 사고 유도
        lost_advantages = [k for k, v in o_eval.items() if v > b_eval[k]]
        
        if lost_advantages:
            adv_text = ", ".join([f"**{a}**" for a in lost_advantages])
            st.warning(f"💡 **기회비용 확인:** {get_josa(best, '을/를')} 선택하면 {other}의 장점인 {adv_text}{get_josa(lost_advantages[-1], '을/를')} 포기하게 됩니다.")
        else:
            st.warning(f"💡 **기회비용 확인:** {get_josa(best, '을/를')} 선택하면 {other}라는 대안 자체를 포기하게 됩니다.")
            
        st.info("⚠️ 최종 결정은 AI가 아닌 여러분의 가치관에 따라 내려야 합니다.")