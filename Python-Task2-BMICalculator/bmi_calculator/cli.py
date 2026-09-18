# -*- coding: utf-8 -*-
"""
Command-Line Interface (CLI) for BMI Calculator.
Meets 100% of Beginner Tier requirements.
"""
import sys
from .calculator import calculate_bmi, classify_bmi, validate_positive_number
from .database import BMIDatabase

def prompt_positive_float(prompt_text: str, field_name: str) -> float:
    """
    Repeatedly prompts the user until a valid positive numeric value is entered.
    Rejects non-numeric, zero, and negative values with helpful error messages.
    """
    while True:
        try:
            raw_input = input(prompt_text).strip()
            # Allow clean exit if user types exit or q
            if raw_input.lower() in ("exit", "quit", "q"):
                print("\nExiting BMI Calculator. Goodbye!")
                sys.exit(0)
                
            val = validate_positive_number(raw_input, field_name)
            return val
        except ValueError as err:
            print(f"[Error] {err}")
            print("Please try again.\n")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled. Goodbye!")
            sys.exit(0)

def display_banner():
    print("=" * 60)
    print("           BODY MASS INDEX (BMI) CALCULATOR           ")
    print("          Oasis Infobyte (OIBSIP) - Task 2            ")
    print("=" * 60)
    print("Type 'exit' or 'q' at any prompt to quit.\n")

def run_cli(save_to_db: bool = True):
    """Main interactive CLI loop."""
    display_banner()
    db = BMIDatabase() if save_to_db else None

    while True:
        print("--- Enter Your Measurements ---")
        user_name_input = input("Enter your name (press Enter for 'Subhajit Samajpati'): ").strip()
        user_name = user_name_input if user_name_input else "Subhajit Samajpati"

        weight_kg = prompt_positive_float("Enter weight in kilograms (kg): ", "Weight")
        height_m = prompt_positive_float("Enter height in meters (e.g., 1.75): ", "Height")

        # Sanity check recommendation for common user mistake (height in cm instead of m)
        if height_m > 3.0:
            print(f"\n[Notice] You entered {height_m} meters. If you meant {height_m} cm, that is {height_m / 100:.2f} m.")
            confirm = input(f"Did you mean {height_m / 100:.2f} meters? (y/n): ").strip().lower()
            if confirm in ("y", "yes"):
                height_m = height_m / 100.0

        try:
            bmi = calculate_bmi(weight_kg, height_m)
            category, advice, _ = classify_bmi(bmi)

            # Display formatted output
            print("\n" + "=" * 45)
            print("                BMI RESULT                   ")
            print("=" * 45)
            print(f" User          : {user_name}")
            print(f" Weight        : {weight_kg:.2f} kg")
            print(f" Height        : {height_m:.2f} m")
            print(f" BMI Value     : {bmi:.2f}")
            print(f" Category      : {category}")
            print("-" * 45)
            print(f" Health Advice : {advice}")
            print("=" * 45)

            # Persist to database
            if db:
                try:
                    db.add_record(weight_kg, height_m, bmi, category, user_name=user_name, notes="CLI Calculation")
                    print(f"(Measurement saved to history database for user: {user_name})")
                except Exception as dberr:
                    print(f"[Warning] Database save failed: {dberr}")

        except Exception as e:
            print(f"[Error] Failed to calculate BMI: {e}")

        # Prompt to continue
        print("\n" + "-" * 45)
        again = input("Would you like to calculate another BMI? (y/n): ").strip().lower()
        print("")
        if again not in ("y", "yes"):
            print("Thank you for using the BMI Calculator. Stay healthy!")
            break

if __name__ == "__main__":
    run_cli()