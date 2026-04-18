import google.generativeai as genai
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
ALT_ENV_PATH = BASE_DIR / ".evn"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
elif ALT_ENV_PATH.exists():
    load_dotenv(dotenv_path=ALT_ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_gemini_model(api_key=None):
    api_key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Gemini API key is not set. Set GEMINI_API_KEY in the environment or pass api_key explicitly."
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


if PYTTSX3_AVAILABLE:
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
    except Exception:
        PYTTSX3_AVAILABLE = False
        engine = None
else:
    engine = None

WAKE_WORD = "rockcee"


def speak(text):
    print("Jarvis:", text)
    if PYTTSX3_AVAILABLE and engine:
        engine.say(text)
        engine.runAndWait()


def take_command():
    if not SR_AVAILABLE:
        return ""
    
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            command = r.recognize_google(audio)
            return command.lower()
        except Exception:
            return ""
    except Exception:
        # Microphone not available in this environment - silently return empty
        return ""


def ask_ai(prompt, api_key=None):
    model = get_gemini_model(api_key)
    response = model.generate_content(prompt)
    return response.text


def handle_command(command, speak_response=False, api_key=None):
    if not command:
        return "No command received."

    normalized = command.lower().strip()
    result = ""

    if WAKE_WORD in normalized:
        normalized = normalized.replace(WAKE_WORD, "").strip()
        result = "System is online. Welcome back Rockstar"

        if "stop" in normalized:
            result = "Shutting down"
        elif "open google" in normalized:
            os.system("open https://www.google.com")
            result = "Opening Google"
        elif "play" in normalized:
            if PYWHATKIT_AVAILABLE:
                pywhatkit.playonyt(normalized)
                result = "Playing on YouTube"
            else:
                result = "YouTube playback not available in this environment."
        else:
            result = ask_ai(normalized, api_key=api_key)
    else:
        if "open google" in normalized:
            os.system("open https://www.google.com")
            result = "Opening Google"
        elif "play" in normalized:
            if PYWHATKIT_AVAILABLE:
                pywhatkit.playonyt(normalized)
                result = "Playing on YouTube"
            else:
                result = "YouTube playback not available in this environment."
        else:
            result = ask_ai(normalized, api_key=api_key)

    if speak_response:
        speak(result)

    return result


def run_jarvis():
    """CLI mode - only for running as a standalone script, not for Streamlit"""
    speak("System is online")
    # Note: This infinite loop is disabled for Streamlit compatibility
    # Use the Streamlit app (app.py) for the interactive interface instead
    # while True:
    #     command = take_command()
    #     if WAKE_WORD in command:
    #         response = handle_command(command, speak_response=True)
    #         if "shutting down" in response.lower():
    #             break
    print("Use 'streamlit run app.py' for the interactive interface")

if __name__ == "__main__":
    # CLI mode - only run when executed directly, not when imported by Streamlit
    try:
        run_jarvis()
    except KeyboardInterrupt:
        print("\nShutting down...")

