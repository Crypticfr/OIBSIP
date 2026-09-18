# -*- coding: utf-8 -*-
"""
Core calculation and classification logic for Body Mass Index (BMI).
"""
from typing import Tuple

def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculates Body Mass Index (BMI).
    Formula: BMI = weight (kg) / (height (m) ^ 2)
    """
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")
    
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def classify_bmi(bmi: float) -> Tuple[str, str, str]:
    """
    Classifies a BMI value into standard WHO health categories.
    Returns: (category, advice_message, color_hex)
    """
    if bmi < 18.5:
        return (
            "Underweight",
            "Your BMI suggests you may be underweight. Consider consulting a healthcare professional for nutritional advice.",
            "#89b4fa"  # Soft Blue
        )
    elif 18.5 <= bmi <= 24.9:
        return (
            "Normal weight",
            "Congratulations! Your BMI is within the healthy weight range. Keep up the balanced diet and active lifestyle!",
            "#a6e3a1"  # Soft Green
        )
    elif 25.0 <= bmi <= 29.9:
        return (
            "Overweight",
            "Your BMI falls into the overweight range. Incorporating regular physical activity and a balanced diet can help.",
            "#fab387"  # Soft Orange / Amber
        )
    else:
        return (
            "Obese",
            "Your BMI indicates obesity, which may increase health risks. We recommend consulting a healthcare provider.",
            "#f38ba8"  # Soft Red
        )

def validate_positive_number(val_str: str, field_name: str = "Value") -> float:
    """
    Validates that an input string represents a positive non-zero number.
    Raises ValueError with a friendly error message on failure.
    """
    if val_str is None or not str(val_str).strip():
        raise ValueError(f"{field_name} cannot be empty.")
    
    cleaned = str(val_str).strip()
    try:
        val = float(cleaned)
    except ValueError:
        raise ValueError(f"Invalid input for {field_name}: '{cleaned}'. Please enter a valid numeric value.")
    
    if val <= 0:
        raise ValueError(f"{field_name} must be greater than 0 (received {val}). Negative numbers and zeros are not allowed.")
        
    return val

def lbs_to_kg(lbs: float) -> float:
    """Converts pounds (lbs) to kilograms (kg)."""
    return lbs * 0.45359237

def inches_to_meters(inches: float) -> float:
    """Converts inches to meters."""
    return inches * 0.0254

def feet_inches_to_meters(feet: float, inches: float = 0.0) -> float:
    """Converts feet and inches to meters."""
    total_inches = (feet * 12.0) + inches
    return inches_to_meters(total_inches)