import streamlit as st
from langchain.chat_models import ChatOpenAI,ChatCohere
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

def get_model():
    opt_paid_free = st.sidebar.radio("Choose Model", ["Free","Paid","Local"], index=0, horizontal=True)
    if opt_paid_free == "Free":
        model_name = st.sidebar.selectbox(label="Select Model", options=["GroqAI", "gemini-2.5-flash-lite", "Command R+"])

        if model_name == "GroqAI":
            groq_key = st.sidebar.text_input("🔑 Groq API Key", type="password")
            if groq_key:
                return ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_key)
            else:
                st.error("Please enter your Groq API Key.")

        elif model_name == "gemini-2.5-flash-lite":
            google_key = st.sidebar.text_input("🔑 Google Gemini API Key", type="password")
            if google_key:
                return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=google_key)
            else:
                st.error("Please enter your Gemini API Key.")

        elif model_name == "Command R+":
            cohere_key = st.sidebar.text_input("🔑 Cohere API Key", type="password")
            if cohere_key:
                return ChatCohere(model="command-r-plus", cohere_api_key=cohere_key)
            else:
                st.error("Please enter your Cohere API Key.")
             
    elif opt_paid_free == "Paid":
        model_name = st.sidebar.selectbox(label="Select Model", options=["GPT-4 Turbo", "Gemini 1.5 Pro", "command-r-plus"])
        if model_name == "GPT-3.5 Turbo":
            openai_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
            if openai_key:
                return ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_key)
            else:
                st.error("Please enter your OpenAI API Key.")

        elif model_name == "GPT-4 Turbo":
            openai_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
            if openai_key:
                return ChatOpenAI(model="gpt-4-turbo", openai_api_key=openai_key)
            else:
                st.error("Please enter your OpenAI API Key.")

        elif model_name == "Gemini 1.5 Pro":
            google_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")
            if google_key:
                return ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_key)
            else:
                st.error("Please enter your Gemini API Key.")

        elif model_name == "command-r-plus":
            cohere_key = st.sidebar.text_input("🔑 Cohere API Key", type="password")
            if cohere_key:
                return ChatCohere(model="command-r-plus", cohere_api_key=cohere_key)
            else:
                st.error("Please enter your Cohere API Key.")

    elif opt_paid_free == "Local":
        local_model_name = st.sidebar.selectbox("Select Local Model", options=["gemma3:latest", "gemma3:1b", "mistral", "custom"])
        
        if local_model_name == "custom":
            model_path = st.sidebar.text_input("Enter custom model name (e.g., my-model)")
        else:
            model_path = local_model_name

        try:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(model=model_path)
        except Exception as e:
            st.error(f"❌ Failed to load local model: {e}")
