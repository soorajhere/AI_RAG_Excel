import streamlit as st
import requests
import base64

st.set_page_config(page_title="Pursuit Chatbot", page_icon="🤖", layout="centered")

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
robot_img_base64 = get_image_base64("robot.png")


# Title and robot image
# Centered image and title using custom HTML
st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{robot_img_base64}' width='100'/>
        <h1>Pursuit Assistant</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input from user
user_input = st.chat_input("Ask about pursuits...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to your backend API
    try:
        response = requests.post("http://localhost:8000/query", json={"query": user_input})
        bot_reply = response.json().get("response", "Sorry, something went wrong.")
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    # Display bot reply
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
