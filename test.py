import streamlit as st
import requests
import json
from datetime import datetime

# Sidebar for additional information
with st.sidebar:
    st.write("Streamlit Azure OpenAI Chatbot")
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot with Azure OpenAI")

# Initialize session state for conversation history and feedback
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "feedback" not in st.session_state:
    st.session_state["feedback"] = []  # Store feedback for each response

# Azure OpenAI API configuration
AZURE_API_KEY = "your_azure_openai_api_key"
AZURE_ENDPOINT = "your_azure_openai_endpoint"
DEPLOYMENT_NAME = "your_deployment_name"

# Function to query Azure OpenAI
def query_azure_openai(prompt):
    url = f"{AZURE_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/completions?api-version=2023-03-15-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_API_KEY,
    }
    payload = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("choices", [{}])[0].get("text", "")
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to query the Azure OpenAI API. {e}"

# Function to log feedback to a text file
def log_feedback(feedback_entry):
    with open("feedback_log.txt", "a") as f:
        f.write(json.dumps(feedback_entry) + "\n")

# Display the conversation history dynamically
for idx, msg in enumerate(st.session_state["messages"]):
    if msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
        
        # Feedback widget for each assistant message
        selected_feedback = st.feedback(options="thumbs", key=f"feedback-{idx}")
        if selected_feedback is not None:
            feedback_entry = {
                "message_idx": idx,
                "timestamp": datetime.now().isoformat(),
                "feedback": "thumbs_up" if selected_feedback == 1 else "thumbs_down",
                "message": msg["content"],
            }
            st.session_state["feedback"].append(feedback_entry)
            log_feedback(feedback_entry)
            st.success("Thank you for your feedback!")
    else:
        st.chat_message("user").write(msg["content"])

# Input prompt from the user
user_input = st.chat_input("You:")

if user_input:
    # Update conversation history
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Create conversation context
    conversation_context = "\n".join(
        [f"{item['role']}: {item['content']}" for item in st.session_state["messages"]]
    )

    # Query the Azure OpenAI API
    response = query_azure_openai(conversation_context)

    # Add the assistant's response to the session state
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # Force UI refresh
    st.rerun()
