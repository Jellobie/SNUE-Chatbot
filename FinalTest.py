import streamlit as st
import random
import time

# [기능/의도 설명형 주석]
# 학생들의 흥미 유발을 위해 앱 상단에 귀여운 동물 아이콘과 제목을 설정함
st.set_page_config(page_title="나는 누구일까요?", page_icon="🐾")

# 퀴즈 데이터: 3학년 과학 교과서에 나오는 동물들의 특징을 단계별 힌트로 구성함
# (CK: 동물의 생김새와 특징 지식)
quiz_data = {
    "개구리": ["나는 물에서도 살고 땅에서도 살아요.", "나는 뒷다리가 튼튼해서 점프를 잘해요.", "어릴 때는 올챙이라고 불려요."],
    "호랑이": ["나는 고양이과 동물이에요.", "몸에 검은색 줄무늬가 있어요.", "산 속의 왕이라고 불려요."],
    "펭귄": ["나는 새지만 날 수 없어요.", "추운 남극에 살아요.", "헤엄을 아주 잘 쳐요."],
    "토끼": ["귀가 아주 길어요.", "깡충깡충 잘 뛰어요.", "당근을 좋아해요."]
}

# 사이드바: 게임 규칙을 설명하여 학생들이 자기주도적으로 활동에 참여하도록 유도함 (PK: 자기주도 학습)
with st.sidebar:
    st.header("🔍 탐구 규칙")
    st.write("1. 챗봇이 동물의 특징을 하나씩 알려줍니다.")
    st.write("2. 설명을 잘 읽고 어떤 동물인지 맞춰보세요.")
    st.write("3. '힌트 줘'라고 입력하면 다음 특징을 알려줍니다.")
    # 게임 초기화 버튼: 새로운 문제로 다시 도전할 수 있게 함
    if st.button("새로운 문제 시작하기"):
        st.session_state.messages = []
        st.session_state.current_animal = None
        st.rerun()

st.title("🐾 나는 누구일까요? (동물 박사 퀴즈)")
st.caption("AI 챗봇이 설명하는 동물의 특징을 듣고 정답을 맞춰보세요!")

# 세션 상태 초기화: 퀴즈 진행 상황과 대화 기록을 유지하기 위함
if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'assistant', 'content': '안녕! 나는 동물 박사야. 지금부터 내가 설명하는 동물이 무엇인지 맞춰봐! (시작하려면 "시작"이라고 말해줘)'}]

# 현재 어떤 동물을 퀴즈로 낼지 결정하지 않았다면 랜덤으로 하나 선택함
if "current_animal" not in st.session_state or st.session_state.current_animal is None:
    st.session_state.current_animal = random.choice(list(quiz_data.keys()))
    st.session_state.hint_step = 0 # 힌트 단계 초기화

# 화면에 기존 대화 내용을 출력하여 학습 흐름을 유지함
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# 사용자 입력 처리
if prompt := st.chat_input("정답을 입력하거나 '힌트'라고 말해보세요."):
    # 사용자 메시지 표시
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # 챗봇 응답 로직 (Rule-based Logic)
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ""
        
        # 정답 확인 로직: 학생이 입력한 단어에 정답 동물이 포함되어 있는지 확인
        target_animal = st.session_state.current_animal
        
        if prompt == "시작":
             assistant_response = f"좋아! 첫 번째 힌트야. \n\n💡 {quiz_data[target_animal][0]}"
        
        elif target_animal in prompt:
            # 정답을 맞혔을 때: 칭찬과 함께 시각적 보상(풍선)을 제공하여 성취감을 높임 (PK: 보상 기제)
            assistant_response = f"정답이야! 👏 나는 '{target_animal}'(이)야. 참 잘했어! \n\n(사이드바의 '새로운 문제 시작하기'를 누르면 또 할 수 있어!)"
            st.balloons() # 스트림릿의 풍선 효과 기능
            
        elif "힌트" in prompt or "모르겠어" in prompt:
            # 힌트 요청 시: 다음 단계의 힌트를 제공하여 비계(Scaffolding) 역할을 수행함
            st.session_state.hint_step += 1
            if st.session_state.hint_step < len(quiz_data[target_animal]):
                assistant_response = f"그럴 수 있어. 더 자세한 힌트를 줄게! \n\n💡 {quiz_data[target_animal][st.session_state.hint_step]}"
            else:
                assistant_response = f"모든 힌트를 다 줬어! 정답은 바로... '{target_animal}'였단다! 다시 도전해볼래?"
        
        else:
            # 오답일 경우: 격려하고 다시 시도하도록 유도함
            assistant_response = "음, 아쉽게도 정답이 아니야. 다시 한번 생각해보거나 '힌트'라고 말해봐!"

        # 타자 치는 효과 구현: 챗봇이 실시간으로 대화하는 듯한 실재감을 줌
        for chunk in assistant_response:
            full_response += chunk
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({'role': 'assistant', 'content': full_response})