import streamlit as st
from openai import OpenAI
from settings import *
import os

# App title
st.set_page_config(page_title="Symtoms Chatbot")

st.markdown(
    """
    <style>
        body {
            background-color: #edf2f7;
            color: #1a202c;
            font-family: 'Open Sans', sans-serif;
        }
        .chat-container {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        }
        .user-message {
            background-color: #fefcbf;
            border-left: 5px solid #f6ad55;
            padding: 10px;
            margin-left: auto;
            width: fit-content;
            border-radius: 5px;
        }
        .assistant-message {
            background-color: #c6f6d5;
            border-left: 5px solid #48bb78;
            padding: 10px;
            border-radius: 5px;
            width: fit-content;
        }
        .stTextInput > div {
            border: 1px solid #cbd5e0;
            border-radius: 6px;
        }
        .stButton button {
            background-color: #3182ce;
            color: white;
            border-radius: 8px;
        }
        .stButton button:hover {
            background-color: #2b6cb0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
# Monster API Client (using the key set from environment variable)
monster_client = OpenAI(
    base_url="https://llm.monsterapi.ai/v1/",
    api_key=str(MONSTER_API_KEY)  # Use the API key set in the environment
)

# Sidebar setup for model selection and parameters
with st.sidebar:
    st.title('Symtoms Chatbot')

    # Model selection
    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Model', ['Meta-Llama', 'Google-Gemma', 'Mistral', 'Microsoft-Phi'])

    model_map = {
        "Meta-Llama": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "Google-Gemma": "google/gemma-2-9b-it",
        "Mistral": "mistralai/Mistral-7B-Instruct-v0.2",
        "Microsoft-Phi": "microsoft/Phi-3-mini-4k-instruct"
    }
    model = model_map[selected_model]

    # Set other parameters
    temperature = st.sidebar.slider('Temperature', 0.01, 2.0, 0.7, 0.01)
    top_p = st.sidebar.slider('Top-p', 0.01, 1.0, 0.9, 0.01)
    max_tokens = st.sidebar.slider('Max Tokens', 64, 148, 120, 8)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
    "role": "assistant", 
    "content": "Give/Explain the symtoms you are having:-"
}]

# Check for rerun trigger and handle it
if "clear_chat_triggered" in st.session_state and st.session_state.clear_chat_triggered:
    st.session_state.clear_chat_triggered = False
    st.experimental_rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [ {"role": "assistant", "content": "You are a helpful assistant specialized in analyzing symptoms and providing basic recommendations. Please only answer questions related to health symptoms, their causes, and possible solutions. Do not answer unrelated queries.If you are asked questions about ny other topic please refrane from answer them "},]
    st.session_state.clear_chat_triggered = True

# Sidebar clear chat button
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating a response from the Monster API
def generate_monster_response(prompt_input):
    # Build up the dialogue context from the session history
    dialogue_history = ""
    for message in st.session_state.messages:
        role = message["role"]
        dialogue_history += f"{role.capitalize()}: {message['content']}\n"

    try:
        # Prepare the API call to Monster API
        response = monster_client.chat.completions.create(
    model=model,
    messages=[
        {"role": "assistant", "content": "You are a helpful assistant specialized in analyzing symptoms and providing basic recommendations. Please only answer questions related to health symptoms, their causes, and possible solutions. Do not answer unrelated queries.If you are asked questions about ny other topic please refrane from answer them"},
        {"role": "user", "content": dialogue_history+prompt_input}
    ],
    temperature=temperature,
    top_p=top_p,
    max_tokens=max_tokens,
    stream=False
)

        # Debug: Print or log the response for inspection
        st.write(response)  # Remove this in production if unnecessary

        # Extract the assistant's response from the API response
        if response.choices and hasattr(response.choices[0].message, "content"):
            return response.choices[0].message.content  # Accessing the content as an attribute
        else:
            return "No response generated. Please try again."

    except Exception as e:
        # Handle and display any errors that occur during the API call
        error_message = f"Error connecting to the Monster API: {e}"
        st.error(error_message)
        # Log the error for debugging
        print(error_message)
        # Return a fallback message
        return "Sorry, I couldn't connect to the API. Please try again later."
    
    
# Handle user input
if prompt := st.chat_input():
    # Add user's prompt to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    # Generate response from Monster API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_monster_response(prompt)  # Get the assistant's response
            st.write(response)

    # Add assistant's response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
