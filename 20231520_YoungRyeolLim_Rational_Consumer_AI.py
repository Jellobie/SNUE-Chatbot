import streamlit as st
import os
from dotenv import load_dotenv

# .env 파일에서 제미나이를 연동하기 위한 코드 
load_dotenv()

# API 키 확인 - Streamlit Cloud의 경우 secrets 사용, 아닐 땐 .env 사용
GOOGLE_API_KEY = None
try:
    # Streamlit Cloud에서는 secrets 사용 (그래서 .env 파일 사용 안 함)
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


# 1. 한국어 조사 자동 처리 함수 (if 문을 통해 자음, 모음 판단하여 은,는,이,가 주격 조사 적용. 자연스러움 확보)
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

# 2. 학생에게 보여지는 메인 화면 및 학습 목표 설정 코드
st.title("🛒 우리 집 '합리적 소비' 매니저")
st.subheader("합리적으로 선택해 보아요.")

# 3. 리스트를 활용하여 주제별 기본 데이터 정의 (교과 내용 CK 연계) 
THEMES = {
    "음식": {"items": ["치킨", "피자", "햄버거", "떡볶이"], "criteria": ["맛", "양", "배달 속도"]},
    "신발": {"items": ["운동화", "구두", "샌들", "슬리퍼"], "criteria": ["디자인", "착용감", "내구성"]},
    "가방": {"items": ["백팩", "에코백", "크로스백", "캐리어"], "criteria": ["디자인", "수납 공간", "무게"]},
    "학용품": {"items": ["연필", "샤프", "볼펜", "만년필"], "criteria": ["디자인", "필기감", "내구성"]}
}

#4. 예산 및 주제 설정 (자원의 희소성 인식)
st.divider()
st.write("### 💰 1단계: 탐구 상황 설정")
col_start1, col_start2 = st.columns(2)
with col_start1:
    choice_theme = st.selectbox("어떤 물건을 사고 싶나요?", list(THEMES.keys()))
with col_start2:
    budget = st.number_input("💵 오늘 쓸 수 있는 최대 예산은? (원)", min_value=0, value=30000, step=1000)

# 5. 선택 기준 추가 (의사결정모형 단계 구현)
st.write("### 📋 2단계: 나만의 선택 기준 만들기")
custom_criteria = st.text_input("기본 기준 외에 추가하고 싶은 기준이 있나요? (예: 브랜드 가치, 환경 보호 등)")
# 학생들이 토의를 통해 정한 새로운 기준을 리스트에 병합하는 코드
final_criteria = THEMES[choice_theme]["criteria"]
if custom_criteria:
    final_criteria = final_criteria + [custom_criteria]
st.info(f"현재 적용된 기준: **{', '.join(final_criteria)}**")

# 6. 대안 입력 및 평가 (TK 구현)
st.divider()
st.write("### 📊 3단계: 대안 평가하기")
col_a, col_b = st.columns(2)

# 대안 A 설정
with col_a:
    st.markdown("#### 🅰️ 대안 A")
    item_a_sel = st.selectbox("후보 선택", THEMES[choice_theme]["items"] + ["직접 입력"], key="item_a_sel")
    item_a = st.text_input("상품 이름", key="item_a_custom") if item_a_sel == "직접 입력" else item_a_sel
    price_a = st.number_input(f"{item_a} 가격 (원)", min_value=0, value=0, key="p_a")
    
    scores_a_val = [st.slider(f"{item_a} - {crit}", 0, 10, 5, key=f"a_{crit}") for crit in final_criteria]
    p_score_a = (1 - (price_a / budget)) * 10 if price_a <= budget and budget > 0 else 0
    st.caption(f"💰 경제성 점수: {p_score_a:.1f}/10점")
    eval_a = dict(zip(final_criteria + ["경제성"], scores_a_val + [p_score_a]))
    avg_a = sum(eval_a.values()) / len(eval_a)

# 대안 B 설정
with col_b:
    st.markdown("#### 🅱️ 대안 B")
    item_b_sel = st.selectbox("후보 선택", THEMES[choice_theme]["items"] + ["직접 입력"], key="item_b_sel")
    item_b = st.text_input("상품 이름", key="item_b_custom") if item_b_sel == "직접 입력" else item_b_sel
    price_b = st.number_input(f"{item_b} 가격 (원)", min_value=0, value=0, key="p_b")
    
    scores_b_val = [st.slider(f"{item_b} - {crit}", 0, 10, 5, key=f"b_{crit}") for crit in final_criteria]
    p_score_b = (1 - (price_b / budget)) * 10 if price_b <= budget and budget > 0 else 0
    st.caption(f"💰 경제성 점수: {p_score_b:.1f}/10점")
    eval_b = dict(zip(final_criteria + ["경제성"], scores_b_val + [p_score_b]))
    avg_b = sum(eval_b.values()) / len(eval_b)

# 7. AI 분석 결과 및 기회비용 리포트
if st.button("🤖 4단계: AI 매니저 분석 결과 보기"):
    if price_a > budget and price_b > budget:
        st.error(f"🚨 예산 내에서 선택 가능한 상품이 없습니다.")
    elif price_a == 0 or price_b == 0:
        st.warning("분석을 위해 가격 정보를 입력해주세요.")
    else:
        st.success("### 📊 AI 매니저의 종합 가치 분석")
        best, other, b_eval, o_eval, b_avg, o_avg = (item_a, item_b, eval_a, eval_b, avg_a, avg_b) if avg_a > avg_b else (item_b, item_a, eval_b, eval_a, avg_b, avg_a)
        st.write(f"✅ AI 추천: **{get_josa(best, '이/가')} {other}보다** 약 **{b_avg - o_avg:.1f}점** 더 합리적입니다.")
        
        lost_adv = [k for k, v in o_eval.items() if v > b_eval[k]]
        if lost_adv:
            prefix = " 및 ".join([f"**{a}**" for a in lost_adv[:-1]])
            last_with_josa = get_josa(lost_adv[-1], "을/를")
            msg = f"{prefix} 및 **{last_with_josa}**" if prefix else f"**{last_with_josa}**"
            st.warning(f"💡 **기회비용 확인:** {get_josa(best, '을/를')} 선택하면 {get_josa(other, '이/가')} 가진 {msg} 포기하게 됩니다.")
        st.info("⚠️ 최종 결정은 AI가 아닌 여러분의 가치관에 따라 내려야 합니다.")