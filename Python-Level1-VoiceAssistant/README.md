# Python Voice Assistant (Beginner Tier)

This is a Python-based voice assistant built as part of the OIBSIP Python Development track.
It listens to spoken commands and responds with useful actions like greetings, telling the time, and performing web searches.

## Features Checklist
- [x] Capture voice input using `speech_recognition` (microphone)
- [x] Respond to "Hello" with a predefined greeting
- [x] Tell the current time and date on request
- [x] Perform a web search on a user-specified topic (open browser with query)
- [x] Graceful error handling: if voice is not understood, ask the user to repeat
- [x] Text-to-speech feedback using `pyttsx3` for all responses
- [x] Modern Graphical User Interface (GUI) built with `tkinter` & `ttk`
- [x] Interactive voice recording button, real-time status indicators, and chat transcript
- [x] Quick action command chips and text entry bar

## Installation

1. Make sure you have Python 3.x installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Graphical User Interface (GUI) - Recommended
To start the assistant with the modern desktop GUI:
```bash
python main.py
```
*Features in GUI mode:*
- **Demo Video Title Card / Splash Screen**: Automatically displays an official internship title card for ~3 seconds on launch displaying **(1) Full Name**, **(2) Assigned Track**, and **(3) Task Title**—satisfying the OIBSIP submission requirement without video editing.
- Click **"Tap to Speak (Mic)"** to record voice commands hands-free.
- Click the **"🔊" (Speaker icon)** next to any message to have the assistant speak it back using `pyttsx3`.
- Use **Quick Command chips** (Hello, Time, Date, Search) for one-click queries.
- Type in the input bar and click **Send** (or press Enter) as a text alternative.
- Live status indicators: `● Ready`, `● Listening...`, `● Processing...`.

To skip the splash screen during testing:
```bash
python main.py --skip-splash
```

### 2. Command-Line Interface (CLI)
If you prefer running in the terminal or in a headless environment:
```bash
python main.py --cli
```

To force text-only input in the terminal without microphone:
```bash
python main.py --text-mode
```

## Running Tests
Run the automated test suite to verify commands and GUI components:
```bash
python -m unittest discover -s tests
```
