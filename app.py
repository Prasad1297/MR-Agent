import streamlit as st
import requests
import json

st.set_page_config(page_title="Market AI Chatbot", layout="wide")

# --- CUSTOM CSS FOR BETTER CHAT STYLING ---
st.markdown("""
    <style>
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        gap: 1rem;
    }
    .chat-message.user {
        background-color: #e3f2fd;
        justify-content: flex-end;
    }
    .chat-message.assistant {
        background-color: #f5f5f5;
    }
    .chat-message.user .content {
        background-color: #2196f3;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        max-width: 70%; 
    }
    .chat-message.assistant .content {
        max-width: 85%;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Market Intelligence Chatbot")
st.markdown("Ask about market trends, competitors, and industry insights")

# --- CONFIG ---
WEBHOOK_URL = "http://127.0.0.1:5678/webhook-test/chat"

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Type your market research question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Get response from n8n
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(
                    WEBHOOK_URL,
                    json={"query": prompt},
                    timeout=120
                )

                if response.status_code == 200:
                    try:
                        data = response.json()

                        # Extract the text response
                        assistant_message = data.get("text", "No response received")

                        # Display it
                        st.markdown(assistant_message)

                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message
                        })

                    except json.JSONDecodeError:
                        st.error("❌ Invalid response from n8n")
                        st.text(response.text)

                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to n8n at {WEBHOOK_URL}")
                st.info("Make sure n8n is running: `n8n start`")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Try a simpler query.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# --- SIDEBAR INFO ---
with st.sidebar:
    st.markdown("### 📊 About This Chatbot")
    st.markdown("""
    This chatbot connects to your n8n workflow to:
    - Research market trends
    - Analyze competitors
    - Extract industry insights
    - Send summaries to Slack
    """)

    st.markdown("### 🔧 Status")
    st.code(WEBHOOK_URL, language="plaintext")
    st.caption("✅ Ready to connect" if WEBHOOK_URL else "❌ No webhook configured")
