# Body Mass Index (BMI) Calculator & Health Tracker

An interactive Python application that calculates a user's Body Mass Index (BMI), categorizes it according to World Health Organization (WHO) standards, and provides tailored health advice.

Developed as **Task 2** of the **Oasis Infobyte (OIBSIP) Python Development Internship**.

---

## Features Checklist

### Beginner Tier
- [x] Prompt user for weight (kg) and height (m) via command line
- [x] Calculate BMI using the standard formula: $\text{BMI} = \frac{\text{weight}}{\text{height}^2}$
- [x] Classify result into standard categories:
  - **Underweight**: $< 18.5$
  - **Normal weight**: $18.5 - 24.9$
  - **Overweight**: $25.0 - 29.9$
  - **Obese**: $\ge 30.0$
- [x] Display the BMI value rounded to 2 decimal places and the category
- [x] Input validation: reject non-numeric inputs, negative values, and zeros with helpful error messages

### Advanced Tier & Extensions
- [x] Modern desktop Graphical User Interface (GUI) built with `tkinter` and `ttk`
- [x] Metric (kg, m/cm) and Imperial (lbs, ft & in) unit conversion toggles
- [x] Visual color-coded gauge and health advice feedback
- [x] SQLite database storage (`bmi_history.db`) for tracking past measurements
- [x] Embedded Matplotlib interactive trend chart displaying user BMI progression over time with colored reference bands
- [x] Built-in Demo Video Title Card Splash Screen (displaying Name, Track, and Task Title for 2.8s) for direct screen recording without video editing

---

## Installation

1. Ensure you have Python 3.8+ installed.
2. Navigate to this project directory:
   ```bash
   cd Python-Task2-BMICalculator
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Graphical User Interface (GUI) - Default
To launch the desktop application:
```bash
python main.py
```
*GUI Highlights:*
- **Title Card Splash**: Automatically shows your details for ~3 seconds on launch—perfect for one-take video screen recordings. (Use `--skip-splash` to bypass).
- **Unit Selector**: Switch between Metric (kg/m) and Imperial (lbs/ft/in).
- **Trend Analytics Tab**: View measurement history table and Matplotlib trend graph with color-coded health zones.

To skip the splash screen during development:
```bash
python main.py --skip-splash
```

### 2. Command-Line Interface (CLI) - Beginner Tier
To run the interactive terminal tool:
```bash
python main.py --cli
```
Example terminal session:
```text
============================================================
           BODY MASS INDEX (BMI) CALCULATOR           
          Oasis Infobyte (OIBSIP) - Level 1           
============================================================
Type 'exit' or 'q' at any prompt to quit.

--- Enter Your Measurements ---
Enter weight in kilograms (kg): 70
Enter height in meters (e.g., 1.75): 1.75

=============================================
                BMI RESULT                   
=============================================
 Weight        : 70.00 kg
 Height        : 1.75 m
 BMI Value     : 22.86
 Category      : Normal weight
---------------------------------------------
 Health Advice : Congratulations! Your BMI is within the healthy weight range. Keep up the balanced diet and active lifestyle!
=============================================
(Measurement saved to history database)

---------------------------------------------
Would you like to calculate another BMI? (y/n): n

Thank you for using the BMI Calculator. Stay healthy!
```

---

## Running Unit Tests

Run the automated test suite verifying calculation formulas, boundary categories, input validation, SQLite persistence, and GUI components:
```bash
python -m unittest discover -s tests
```