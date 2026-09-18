import sys

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("Warning: speech_recognition not found. Falling back to text input.", file=sys.stderr)

def listen(text_mode: bool = False) -> str:
    """
    Listens to the microphone and returns the recognized text.
    If text_mode is True, or if speech_recognition is unavailable, falls back to standard input.
    Returns an empty string if nothing could be recognized.
    """
    if text_mode or not SR_AVAILABLE:
        try:
            return input("You (text input): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "exit"

    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Listening...")
            # Adjust for ambient noise briefly
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Listen to the user
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Recognizing...")
            # Use Google Web Speech API (free, requires internet)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
    except sr.WaitTimeoutError:
        print("Timeout: No speech detected.")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio.")
        # We will handle asking to repeat in the command layer
        return "ERROR_UNKNOWN"
    except sr.RequestError as e:
        print(f"Could not request results; check your internet connection: {e}")
        return "ERROR_REQUEST"
    except OSError as e:
        print(f"Microphone error: {e}. Falling back to text mode.")
        return listen(text_mode=True)
    except Exception as e:
        print(f"An unexpected error occurred during speech recognition: {e}")
        if "PyAudio" in str(e):
            print("PyAudio is required for microphone usage. Falling back to text mode.")
            return listen(text_mode=True)
        return ""
    except AttributeError as e:
        print(f"An unexpected error occurred during speech recognition: {e}")
        if "PyAudio" in str(e):
            print("PyAudio is required for microphone usage. Falling back to text mode.")
            return listen(text_mode=True)
        return ""
