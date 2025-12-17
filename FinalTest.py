import streamlit as st
import random
import time

# [기능/의도 설명형 주석]
# 학생들의 흥미 유발을 위해 앱 상단에 귀여운 동물 아이콘과 제목을 설정함
st.set_page_config(page_title="나는 누구일까요?", page_icon="🐾")

# 퀴즈 데이터: 3학년 과학 교과서에 나오는 동물들의 특징 (CK)
quiz_data = {
    "개구리": ["나는 물에서도 살고 땅에서도 살아요.", "나는 뒷다리가 튼튼해서 점프를 잘해요.", "어릴 때는 올챙이라고 불려요."],
    "호랑이": ["나는 고양이과 동물이에요.", "몸에 검은색 줄무늬가 있어요.", "산 속의 왕이라고 불려요."],
    "펭귄": ["나는 새지만 날 수 없어요.", "추운 남극에 살아요.", "헤엄을 아주 잘 쳐요."],
    "토끼": ["귀가 아주 길어요.", "깡충깡충 잘 뛰어요.", "당근을 좋아해요."]
}

# [기능 추가] 정답 시 보여줄 동물 이미지 URL 사전
# 정답을 맞혔을 때 시각적 보상을 제공하여 학습 효과를 높임 (TK)
image_data = {
    "개구리": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Atelopus_zeteki1.jpg/440px-Atelopus_zeteki1.jpg",
    "호랑이": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Walking_tiger_female.jpg/640px-Walking_tiger_female.jpg",
    "펭귄": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Emperor_Penguin_Manchot_empereur.jpg/440px-Emperor_Penguin_Manchot_empereur.jpg",
    "토끼": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Oryctolagus_cuniculus_Rcdo.jpg/440px-Oryctolagus_cuniculus_Rcdo.jpg"
}

# 사이드바: 게임 규칙 설명 및 리셋 기능
with st.sidebar:
    st.header("🔍 탐구 규칙")
    st.write("1. 챗봇이 동물의 특징을 하나씩 알려줍니다.")
    st.write("2. 설명을 잘 읽고 어떤 동물인지 맞춰보세요.")
    st.write("3. '힌트 줘'라고 입력하면 다음 특징을 알려줍니다.")
    
    # [버그 수정]
    # 버튼 클릭 시 대화 기록을 빈 리스트가 아닌 '초기 인사말'이 담긴 리스트로 초기화함
    if st.button("새로운 문제 시작하기"):
        st.session_state.messages = [{'role': 'assistant', 'content': '안녕! 나는 동물 박사야. 지금부터 내가 설명하는 동물이 무엇인지 맞춰봐! (시작하려면 "시작"이라고 말해줘)'}]
        st.session_state.current_animal = None
        st.session_state.hint_step = 0
        st.rerun()

# [UI 개선] 제목에 줄바꿈(\n)을 넣어 모바일이나 좁은 화면에서도 가독성을 높임
st.title("🐾 나는 누구일까요?\n(동물 박사 퀴즈)")
st.caption("AI 챗봇이 설명하는 동물의 특징을 듣고 정답을 맞춰보세요!")

# 세션 상태 초기화: 앱이 처음 실행될 때 기본 변수들을 설정함
if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'assistant', 'content': '안녕! 나는 동물 박사야. 지금부터 내가 설명하는 동물이 무엇인지 맞춰봐! (시작하려면 "시작"이라고 말해줘)'}]

# 현재 문제가 없다면 새로운 문제를 랜덤으로 출제함
if "current_animal" not in st.session_state or st.session_state.current_animal is None:
    st.session_state.current_animal = random.choice(list(quiz_data.keys()))
    st.session_state.hint_step = 0 

# 화면에 기존 대화 내용을 출력 (UI 유지)
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
        # [기능 추가] 만약 메시지에 이미지가 포함되어 있다면(image_url 키가 있다면) 이미지 출력
        if 'image_url' in message:
             st.image(message['image_url'], width=300)

# 사용자 입력 처리
if prompt := st.chat_input("정답을 입력하거나 '힌트'라고 말해보세요."):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ""
        
        target_animal = st.session_state.current_animal
        show_image = False # 이미지를 보여줄지 여부 결정 변수
        
        # 1. 시작 명령어 처리
        if prompt == "시작":
             assistant_response = f"좋아! 첫 번째 힌트야. \n\n💡 {quiz_data[target_animal][0]}"
        
        # 2. 정답 처리
        elif target_animal in prompt:
            assistant_response = f"정답이야! 👏 나는 '{target_animal}'(이)야. 참 잘했어! \n\n(아래 사진을 봐! 정말 귀엽지?)"
            st.balloons() 
            show_image = True # 정답이므로 이미지를 보여주도록 설정
            
        # 3. 힌트 요청 처리
        elif "힌트" in prompt or "모르겠어" in prompt:
            st.session_state.hint_step += 1
            if st.session_state.hint_step < len(quiz_data[target_animal]):
                assistant_response = f"그럴 수 있어. 더 자세한 힌트를 줄게! \n\n💡 {quiz_data[target_animal][st.session_state.hint_step]}"
            else:
                assistant_response = f"모든 힌트를 다 줬어! 정답은 바로... '{target_animal}'였단다! 다시 도전해볼래?"
                show_image = True # 못 맞췄더라도 정답 공개 시 이미지 보여줌
        
        # 4. 오답 처리
        else:
            assistant_response = "음, 아쉽게도 정답이 아니야. 다시 한번 생각해보거나 '힌트'라고 말해봐!"

        # 타자 효과 출력
        for chunk in assistant_response:
            full_response += chunk
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        # [기능 추가] 정답을 맞히거나 힌트가 끝났을 때 이미지 출력
        if show_image:
            st.image(image_data[target_animal], width=300)
            # 대화 기록에 저장할 때 이미지 정보도 같이 저장 (나중에 다시 볼 때도 나오게 함)
            st.session_state.messages.append({'role': 'assistant', 'content': full_response, 'image_url': image_data[target_animal]})
        else:
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})