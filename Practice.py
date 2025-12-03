import streamlit as st
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="Gemini 챗봇", page_icon="🤖")

# API 키 확인
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_api_key_here":
    st.error("⚠️ .env 파일에 GOOGLE_API_KEY를 설정해주세요!")
    st.stop()

# 제목
st.title("🤖 Gemini 챗봇")
st.caption("Google Gemini API를 사용하는 챗봇입니다")

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}]

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gemini API 호출
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("생성 중...")
        
        try:
            # Gemini API 요청
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini2.5-flash:generateContent?key={GOOGLE_API_KEY}"
            
            # 대화 기록을 Gemini API 형식으로 변환
            contents = []
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
                elif msg["role"] == "assistant":
                    contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
            
            payload = {
                "contents": contents
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            # 응답 파싱
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                assistant_response = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                assistant_response = "죄송합니다. 응답을 생성할 수 없습니다."
            
            message_placeholder.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
        except requests.exceptions.RequestException as e:
            error_message = f"❌ API 요청 중 오류가 발생했습니다: {str(e)}"
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
        except Exception as e:
            error_message = f"❌ 오류가 발생했습니다: {str(e)}"
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})