import datetime
import webbrowser
import re
from .tts import speak

def handle_greeting(command: str) -> bool:
    """Handles basic greetings."""
    greetings = [r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bgood morning\b', r'\bgood afternoon\b', r'\bgood evening\b']
    if any(re.search(greet, command, re.IGNORECASE) for greet in greetings):
        hour = datetime.datetime.now().hour
        if hour < 12:
            speak("Good morning! How can I help you today?")
        elif 12 <= hour < 18:
            speak("Good afternoon! How can I help you today?")
        else:
            speak("Good evening! How can I help you today?")
        return True
    return False

def handle_datetime(command: str) -> bool:
    """Handles requests for current date or time."""
    cmd_lower = command.lower()
    if "time" in cmd_lower:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")
        return True
    elif "date" in cmd_lower:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}.")
        return True
    return False

def handle_search(command: str) -> bool:
    """Handles web search requests."""
    search_prefixes = [
        "open google and search for",
        "open google and search",
        "search google for",
        "search on google for",
        "search on google",
        "search the web for",
        "search web for",
        "search for",
        "search",
        "google",
        "look up",
    ]
    
    cleaned_command = command.strip()
    
    for prefix in search_prefixes:
        match = re.search(rf'\b{re.escape(prefix)}(?:\s+(.*))?$', cleaned_command, re.IGNORECASE)
        if match:
            query = match.group(1)
            query = query.strip() if query else ""
            if query:
                # Optionally clean up trailing polite phrases
                query = re.sub(r'\b(please|for me)\b', '', query, flags=re.IGNORECASE).strip()
            if query:
                speak(f"Searching the web for {query}")
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(url)
                return True
            else:
                speak("What would you like me to search for?")
                return True
    return False

def process_command(command: str) -> bool:
    """
    Processes the given command and returns True if the application should exit.
    """
    if command == "ERROR_UNKNOWN":
        speak("I couldn't quite catch that. Could you please repeat?")
        return False
    elif command == "ERROR_REQUEST":
        speak("I'm having trouble connecting to the speech recognition service. Please check your internet.")
        return False
    elif not command:
        # Empty command (timeout or silence)
        return False

    # Check for exit commands
    exit_commands = [r'\bexit\b', r'\bquit\b', r'\bstop\b', r'\bgoodbye\b', r'\bbye\b']
    if any(re.search(cmd, command, re.IGNORECASE) for cmd in exit_commands):
        speak("Goodbye! Have a great day.")
        return True

    # Try handlers in order
    if handle_greeting(command):
        return False
    if handle_datetime(command):
        return False
    if handle_search(command):
        return False

    # Fallback for unrecognized text
    speak("I'm not sure how to help with that yet.")
    return False
