import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(page_title="MoSPI Chatbot", page_icon="🤖")
st.title("MoSPI RAG Chatbot")
st.markdown("Ask me anything about the MoSPI reports!")

# --- API Configuration ---
API_URL = "http://127.0.0.1:8000/query"

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages from History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
if user_query := st.chat_input("Enter your query here..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Prepare data for API request
    payload = {"query": user_query}

    with st.spinner("Thinking..."):
        try:
            # Send POST request to your FastAPI API
            response = requests.post(API_URL, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Get the response from the API
            api_response = response.json()
            chatbot_response = api_response.get("answer", "I'm sorry, I couldn't get a response from the model.")
            
        except requests.exceptions.RequestException as e:
            chatbot_response = f"Error: The backend API is not running. Please start the FastAPI server first. Details: {e}"

    # Display chatbot response in chat message container
    with st.chat_message("assistant"):
        st.markdown(chatbot_response)
    # Add chatbot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": chatbot_response})