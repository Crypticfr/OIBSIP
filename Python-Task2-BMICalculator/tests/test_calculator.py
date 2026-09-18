# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
from bmi_calculator.calculator import (
    calculate_bmi,
    classify_bmi,
    validate_positive_number,
    lbs_to_kg,
    inches_to_meters,
    feet_inches_to_meters
)
from bmi_calculator.database import BMIDatabase

class TestBMICalculator(unittest.TestCase):

    def test_calculate_bmi(self):
        """Test standard BMI calculation with rounding to 2 decimal places."""
        # 70 kg, 1.75 m -> 70 / (1.75^2) = 22.85714 -> 22.86
        self.assertEqual(calculate_bmi(70, 1.75), 22.86)
        # 50 kg, 1.60 m -> 50 / 2.56 = 19.53125 -> 19.53
        self.assertEqual(calculate_bmi(50, 1.60), 19.53)
        # 95 kg, 1.80 m -> 95 / 3.24 = 29.32098 -> 29.32
        self.assertEqual(calculate_bmi(95, 1.80), 29.32)

    def test_calculate_bmi_invalid_values(self):
        """Test that non-positive height or weight raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_bmi(70, 0)
        with self.assertRaises(ValueError):
            calculate_bmi(70, -1.75)
        with self.assertRaises(ValueError):
            calculate_bmi(0, 1.75)
        with self.assertRaises(ValueError):
            calculate_bmi(-70, 1.75)

    def test_classify_bmi_categories(self):
        """Test WHO standard category boundaries."""
        # Underweight (< 18.5)
        cat, _, _ = classify_bmi(16.0)
        self.assertEqual(cat, "Underweight")
        cat, _, _ = classify_bmi(18.49)
        self.assertEqual(cat, "Underweight")

        # Normal weight (18.5 - 24.9)
        cat, _, _ = classify_bmi(18.5)
        self.assertEqual(cat, "Normal weight")
        cat, _, _ = classify_bmi(22.0)
        self.assertEqual(cat, "Normal weight")
        cat, _, _ = classify_bmi(24.9)
        self.assertEqual(cat, "Normal weight")

        # Overweight (25.0 - 29.9)
        cat, _, _ = classify_bmi(25.0)
        self.assertEqual(cat, "Overweight")
        cat, _, _ = classify_bmi(28.3)
        self.assertEqual(cat, "Overweight")
        cat, _, _ = classify_bmi(29.9)
        self.assertEqual(cat, "Overweight")

        # Obese (>= 30.0)
        cat, _, _ = classify_bmi(30.0)
        self.assertEqual(cat, "Obese")
        cat, _, _ = classify_bmi(35.5)
        self.assertEqual(cat, "Obese")

    def test_validate_positive_number(self):
        """Test input validation for non-numeric, negative, and zero inputs."""
        # Valid cases
        self.assertEqual(validate_positive_number("75.5", "Weight"), 75.5)
        self.assertEqual(validate_positive_number(" 1.80 ", "Height"), 1.80)

        # Invalid: strings / non-numeric
        with self.assertRaises(ValueError) as ctx:
            validate_positive_number("abc", "Weight")
        self.assertIn("Invalid input for Weight", str(ctx.exception))

        with self.assertRaises(ValueError):
            validate_positive_number("", "Height")

        # Invalid: zero or negative
        with self.assertRaises(ValueError) as ctx:
            validate_positive_number("-5", "Weight")
        self.assertIn("must be greater than 0", str(ctx.exception))

        with self.assertRaises(ValueError):
            validate_positive_number("0", "Height")

    def test_unit_conversions(self):
        """Test lbs to kg and feet/inches to meters conversion."""
        # 150 lbs = 68.0388 kg
        self.assertAlmostEqual(lbs_to_kg(150), 68.0388, places=3)
        # 5 feet 10 inches = 70 inches = 1.778 meters
        self.assertAlmostEqual(feet_inches_to_meters(5, 10), 1.778, places=3)
        self.assertAlmostEqual(inches_to_meters(12), 0.3048, places=4)

    def test_database_crud(self):
        """Test SQLite database record persistence, retrieval, and clear."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            temp_db = tf.name

        try:
            db = BMIDatabase(db_path=temp_db)
            self.assertEqual(len(db.get_all_records()), 0)

            # Insert
            id1 = db.add_record(70.0, 1.75, 22.86, "Normal weight")
            id2 = db.add_record(85.0, 1.75, 27.76, "Overweight")
            self.assertGreater(id2, id1)

            records = db.get_all_records()
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["bmi"], 27.76)  # Newest first

            chrono = db.get_chronological_records()
            self.assertEqual(chrono[0]["bmi"], 22.86)  # Oldest first

            # Delete single record
            deleted = db.delete_record(id1)
            self.assertTrue(deleted)
            self.assertEqual(len(db.get_all_records()), 1)

            # Clear all
            db.clear_history()
            self.assertEqual(len(db.get_all_records()), 0)
        finally:
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception:
                    pass

    def test_database_multi_user(self):
        """Test multi-user record isolation and filtering."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            temp_db = tf.name

        try:
            db = BMIDatabase(db_path=temp_db)

            # Insert for Alice and Bob
            db.add_record(60.0, 1.65, 22.04, "Normal weight", user_name="Alice")
            db.add_record(62.0, 1.65, 22.77, "Normal weight", user_name="Alice")
            db.add_record(90.0, 1.80, 27.78, "Overweight", user_name="Bob")

            # Check distinct users
            users = db.get_users()
            self.assertIn("Alice", users)
            self.assertIn("Bob", users)

            # Filter by user
            alice_records = db.get_all_records(user_name="Alice")
            self.assertEqual(len(alice_records), 2)
            for r in alice_records:
                self.assertEqual(r["user_name"], "Alice")

            bob_records = db.get_all_records(user_name="Bob")
            self.assertEqual(len(bob_records), 1)
            self.assertEqual(bob_records[0]["user_name"], "Bob")

            # Clear only Alice's records
            db.clear_history(user_name="Alice")
            self.assertEqual(len(db.get_all_records(user_name="Alice")), 0)
            self.assertEqual(len(db.get_all_records(user_name="Bob")), 1)
        finally:
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception:
                    pass

    def test_database_error_handling(self):
        """Test that invalid operations or paths raise DatabaseError cleanly."""
        from bmi_calculator.database import DatabaseError
        # Invalid directory path
        invalid_path = "Z:\\non_existent_dir_999\\test.db"
        with self.assertRaises(DatabaseError):
            BMIDatabase(db_path=invalid_path)

if __name__ == '__main__':
    unittest.main()