# Oasis Infobyte Internship — Python Development Track (OIBSIP)

**Candidate Name**: Subhajit Samajpati  
**Domain**: Python Development  
**Organization**: [Oasis Infobyte](https://oasisinfobyte.com/)  

---

## 📂 Repository Structure

```text
OIBSIP/
├── Python-Task1-VoiceAssistant/     # Task 1: Desktop Voice Assistant (CLI & GUI with TTS)
└── Python-Task2-BMICalculator/       # Task 2: Body Mass Index (BMI) Calculator & Analytics
```

---

## 🚀 Projects Overview

### [Task 1: Desktop Voice Assistant](./Python-Task1-VoiceAssistant)
- **Features**:
  - Voice and text command recognition with offline-ready architecture.
  - Speech synthesis powered by thread-safe `pyttsx3`.
  - Modern Tkinter desktop GUI with dark theme and live transcription.
  - Interactive `🔊` talkback speech playback button for any message.
  - Case-insensitive natural command processing (greetings, time/date check, web search, wikipedia lookups).
  - Built-in 2.8s internship title card splash screen tailored for video recording.
- **Run**:
  ```bash
  cd Python-Task1-VoiceAssistant
  python main.py
  ```

---

### [Task 2: BMI Calculator & Health Analytics](./Python-Task2-BMICalculator)
- **Features**:
  - Dual-mode architecture: Interactive CLI (`--cli`) and full-featured desktop Tkinter GUI.
  - Accurate WHO Body Mass Index calculation ($\text{BMI} = \frac{\text{weight}}{\text{height}^2}$) with 4 classifications: Underweight, Normal, Overweight, Obese.
  - Real-time color-coded health gauge and classification feedback.
  - Multi-user profile management with distinct user switcher.
  - SQLite database persistence (`bmi_records`) with timestamps, unit tracking, and secure connection lifecycle management.
  - Matplotlib trend analytics with WHO reference bands and user-specific trend lines.
  - Metric (kg / cm) and Imperial (lbs / ft-in) instant unit toggles with automatic conversion.
  - Built-in 2.8s internship title card splash screen.
- **Run**:
  ```bash
  cd Python-Task2-BMICalculator
  # Launch Desktop GUI
  python main.py

  # Launch Terminal CLI
  python main.py --cli
  ```

---

## 🧪 Testing

Both projects include comprehensive automated test suites:
```bash
# Task 1 Tests (12 tests)
cd Python-Task1-VoiceAssistant
python -m unittest discover -s tests

# Task 2 Tests (15 tests)
cd Python-Task2-BMICalculator
python -m unittest discover -s tests
```
