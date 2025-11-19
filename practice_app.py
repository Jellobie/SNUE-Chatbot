import streamlit as st
import random
import time

st.write ("나는 서울교대 챗봇이야")

st.caption ("수업에서 배운 내용만 답변 가능")
if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'assistant', 'content': '안녕하세요! 무엇을 도와드릴까요?'}]

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = random.choice(["네, 알겠습니다.", "그렇군요.", "그럼 이제 무엇을 도와드릴까요?"])
        
        # 응답을 타자 효과와 함께 표시
        for chunk in assistant_response:
            full_response += chunk
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({'role': 'assistant', 'content': full_response})