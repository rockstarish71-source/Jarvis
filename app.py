import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from jarvis import handle_command, PYTTSX3_AVAILABLE

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
ALT_ENV_PATH = BASE_DIR / ".evn"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
elif ALT_ENV_PATH.exists():
    load_dotenv(dotenv_path=ALT_ENV_PATH)

st.set_page_config(page_title="Jarvis AI", page_icon="🤖")

st.title("Jarvis AI Streamlit")
st.markdown(
    "Use the Jarvis command interface to open Google, play YouTube videos, or ask Gemini AI questions. "
    "Type a command and press Run."
)

env_api_key = os.getenv("GEMINI_API_KEY")
api_key_input = st.text_input(
    "Gemini API key",
    type="password",
    placeholder="Leave blank to use GEMINI_API_KEY from environment",
)

if env_api_key:
    st.success("GEMINI_API_KEY is loaded from the environment.")
elif not api_key_input:
    st.error(
        "No Gemini API key found. Enter a key above or set GEMINI_API_KEY and refresh."
    )

command = st.text_area(
    "Command",
    placeholder='e.g. "rockcee open google" or "play never gonna give you up" or "What is the fastest land animal?"',
    height=120,
)

use_speech = st.checkbox("Speak response", value=False, disabled=not PYTTSX3_AVAILABLE)
if not PYTTSX3_AVAILABLE:
    st.info("Text-to-speech is not available in this environment.")

if st.button("Run Jarvis"):
    if not command.strip():
        st.warning("Please enter a command before running Jarvis.")
    else:
        api_key = api_key_input.strip() or env_api_key
        if not api_key:
            st.error("Gemini API key is required to run Jarvis.")
        else:
            with st.spinner("Processing command..."):
                try:
                    response = handle_command(command, speak_response=use_speech, api_key=api_key)
                except EnvironmentError as exc:
                    st.error(str(exc))
                    response = None

            if response is not None:
                st.subheader("Jarvis response")
                st.write(response)
                if use_speech and PYTTSX3_AVAILABLE:
                    st.info("Audio response was sent to the local text-to-speech engine.")
